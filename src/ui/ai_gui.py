"""
AI Assistant GUI
GUI for main_ai.py - AI-Powered Features
Webpage Analysis, Code Analysis, AI responses
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread

from src.core.logger import setup_logger
from .base_gui import BaseAssistantGUI
from .styles import get_icon, QUICK_COMMANDS, get_color, get_font, apply_ttk_theme

logger = setup_logger(__name__)


class AIAssistantGUI(BaseAssistantGUI):
    """
    GUI for AI Voice Assistant (main_ai.py)
    
    Features:
    - Wake/Sleep control
    - AI webpage analysis
    - AI code analysis
    - Navigation & search
    - Analysis results display
    """

    def __init__(self, assistant=None):
        """Initialize AI Assistant GUI"""
        super().__init__(assistant=assistant, mode="ai")
        self.analysis_results = []
        logger.info("AIAssistantGUI initialized")

    def _build_control_panel(self, parent):
        """Build control panel for AI assistant"""
        # Header
        section_header = tk.Label(
            parent,
            text="🧠 AI Control Center",
            font=get_font("heading"),
            fg=get_color("accent"),
            bg=get_color("bg_secondary"),
        )
        section_header.pack(anchor="w", pady=(0, 10))

        # Control frame
        ctrl_frame = tk.Frame(
            parent,
            bg=get_color("bg_tertiary"),
            highlightthickness=1,
            highlightbackground=get_color("panel_border"),
        )
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        inner = tk.Frame(ctrl_frame, bg=get_color("bg_tertiary"))
        inner.pack(fill=tk.X, padx=14, pady=14)

        # Wake button
        self.btn_wake = tk.Button(
            inner,
            text=f"{get_icon('wake')}  Wake Up",
            command=self._on_wake,
            bg=get_color("accent"),
            activebackground=get_color("accent_light"),
            fg="#08111f",
            font=get_font("heading"),
            padx=20,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
        )
        self.btn_wake.pack(fill=tk.X, pady=(0, 8))

        # Sleep button
        self.btn_sleep = tk.Button(
            inner,
            text=f"{get_icon('sleep_action')}  Sleep",
            command=self._on_sleep,
            bg=get_color("warning"),
            activebackground="#fbbf24",
            fg="#08111f",
            font=get_font("heading"),
            padx=20,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            state=tk.DISABLED,
        )
        self.btn_sleep.pack(fill=tk.X, pady=(0, 10))

        # Status label
        tk.Label(
            inner,
            text="Status:",
            font=get_font("subheading"),
            fg=get_color("fg_secondary"),
            bg=get_color("bg_tertiary"),
        ).pack(anchor="w", pady=(8, 4))

        self.current_status = tk.Label(
            inner,
            text="🔴 Sleeping",
            font=get_font("normal"),
            fg=get_color("warning"),
            bg=get_color("bg_tertiary"),
        )
        self.current_status.pack(anchor="w", pady=(0, 0))

    def _build_output_section(self, parent):
        """Build output section with tabs for different types"""
        section_header = tk.Label(
            parent,
            text=f"{get_icon('console')} Output & Analysis",
            font=get_font("heading"),
            fg=get_color("accent"),
            bg=get_color("bg_secondary"),
        )
        section_header.pack(anchor="w", pady=(0, 10))

        shell = tk.Frame(
            parent,
            bg=get_color("bg_tertiary"),
            highlightthickness=1,
            highlightbackground=get_color("panel_border"),
        )
        shell.pack(fill=tk.BOTH, expand=True)

        shell_inner = tk.Frame(shell, bg=get_color("bg_tertiary"))
        shell_inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        # Create tabs
        apply_ttk_theme(parent.winfo_toplevel())
        notebook = ttk.Notebook(shell_inner)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Console tab
        console_frame = tk.Frame(notebook, bg=get_color("bg_secondary"))
        notebook.add(console_frame, text=f"{get_icon('console')} Console")

        self.console = scrolledtext.ScrolledText(
            console_frame,
            bg=get_color("console_bg"),
            fg=get_color("console_fg"),
            font=get_font("console"),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
            insertbackground=get_color("fg_primary"),
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Configure tags
        self.console.tag_configure("info", foreground=get_color("info"))
        self.console.tag_configure("success", foreground=get_color("success"))
        self.console.tag_configure("warning", foreground=get_color("warning"))
        self.console.tag_configure("error", foreground=get_color("error"))

        # Analysis tab
        analysis_frame = tk.Frame(notebook, bg=get_color("bg_secondary"))
        notebook.add(analysis_frame, text=f"{get_icon('analyze')} Analysis Results")

        self.analysis_output = scrolledtext.ScrolledText(
            analysis_frame,
            bg=get_color("bg_quaternary"),
            fg=get_color("fg_primary"),
            font=get_font("normal"),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
        )
        self.analysis_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Summary tab
        summary_frame = tk.Frame(notebook, bg=get_color("bg_secondary"))
        notebook.add(summary_frame, text=f"{get_icon('summarize')} Summaries")

        self.summary_output = scrolledtext.ScrolledText(
            summary_frame,
            bg=get_color("bg_quaternary"),
            fg=get_color("fg_primary"),
            font=get_font("normal"),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=0,
        )
        self.summary_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def _get_quick_commands(self) -> list:
        """Get quick command buttons for AI assistant"""
        return QUICK_COMMANDS.get("ai", [])

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers
    # ─────────────────────────────────────────────────────────────────────────

    def _on_wake(self):
        """Handle wake button click"""
        if not self.assistant:
            self.log_console("❌ Assistant not connected", "error")
            return

        try:
            self.assistant.is_awake = True
            self.btn_wake.config(state=tk.DISABLED)
            self.btn_sleep.config(state=tk.NORMAL)
            self._update_status_awake()
            self.current_status.config(text="🟢 Awake", fg=get_color("success"))
            self.log_console("✓ AI Assistant woke up!", "success")

            # Speak greeting
            if hasattr(self.assistant, 'speaker'):
                Thread(
                    target=lambda: self.assistant.speaker.speak_greeting(),
                    daemon=True
                ).start()

        except Exception as e:
            self.log_console(f"❌ Error waking up: {e}", "error")
            logger.error(f"Wake error: {e}", exc_info=True)

    def _on_sleep(self):
        """Handle sleep button click"""
        if not self.assistant:
            self.log_console("❌ Assistant not connected", "error")
            return

        try:
            self.assistant.is_awake = False
            self.btn_wake.config(state=tk.NORMAL)
            self.btn_sleep.config(state=tk.DISABLED)
            self._update_status_sleeping()
            self.current_status.config(text="🔴 Sleeping", fg=get_color("warning"))
            self.log_console("😴 AI Assistant going to sleep", "warning")

            # Speak message
            if hasattr(self.assistant, 'speaker'):
                Thread(
                    target=lambda: self.assistant.speaker.speak(
                        "Going to sleep. Say hey assistant to wake me."
                    ),
                    daemon=True
                ).start()

        except Exception as e:
            self.log_console(f"❌ Error going to sleep: {e}", "error")
            logger.error(f"Sleep error: {e}", exc_info=True)

    def _send_command_direct(self, command: str):
        """Send command to AI assistant"""
        if not self.assistant:
            self.log_console("❌ Assistant not connected", "error")
            return

        self.log_console(f"👤 You: {command}", "info")

        # Process in thread to not block UI
        def process():
            try:
                # Parse command
                parsed = self.assistant.parser.parse(command, context=None)
                intent = parsed.get("intent", "unknown")
                params = parsed.get("params", {})

                self.log_console(f"🔍 Intent: {intent}", "info")

                # Handle command
                result = self.assistant.handle_command(intent, params)

                # Log result
                if result:
                    self.log_console(f"✓ Command executed", "success")

            except Exception as e:
                self.log_console(f"❌ Error: {e}", "error")
                logger.error(f"Command error: {e}", exc_info=True)

        thread = Thread(target=process, daemon=True)
        thread.start()

    # ─────────────────────────────────────────────────────────────────────────
    # Analysis Output Methods
    # ─────────────────────────────────────────────────────────────────────────

    def log_analysis(self, message: str):
        """Log to analysis tab"""
        self.analysis_output.insert(tk.END, f"{message}\n")
        self.analysis_output.see(tk.END)
        self.root.update()

    def log_summary(self, message: str):
        """Log to summary tab"""
        self.summary_output.insert(tk.END, f"{message}\n")
        self.summary_output.see(tk.END)
        self.root.update()
