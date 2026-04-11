"""
Base GUI Class - Abstract foundation for all Assistant GUIs
Handles common UI elements and event management
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from threading import Thread
from pathlib import Path
import time

from src.core.logger import setup_logger
from .styles import COLORS, FONTS, UI_CONFIG, ICONS, get_color, get_font, get_icon

logger = setup_logger(__name__)


class BaseAssistantGUI:
    """
    Base GUI class for Voice Assistant
    Provides common UI components and event handling
    
    Subclasses should implement:
    - _build_control_panel()
    - _get_quick_commands()
    """

    def __init__(self, assistant=None, mode="basic"):
        """
        Initialize base GUI
        
        Args:
            assistant: Reference to assistant instance (main.py or main_ai.py)
            mode: "basic" or "ai"
        """
        self.assistant = assistant
        self.mode = mode
        self.root = tk.Tk()
        
        # Configure window
        self.root.title(UI_CONFIG["window_title"])
        self.root.geometry(f"{UI_CONFIG['window_width']}x{UI_CONFIG['window_height']}")
        self.root.configure(bg=get_color("bg_primary"))
        
        if UI_CONFIG["always_on_top"]:
            self.root.attributes("-topmost", True)
        
        logger.info(f"BaseAssistantGUI initialized (mode={mode})")
        
        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Build complete UI layout"""
        self._build_header()
        self._build_main_content()
        self._build_footer()

    def _build_header(self):
        """Build top header with title and status"""
        header = tk.Frame(
            self.root,
            bg=get_color("header_bg"),
            height=80
        )
        header.pack(fill=tk.X, pady=0)

        # Title
        title = tk.Label(
            header,
            text=f"{get_icon('awake')} Voice Assistant",
            font=get_font("title"),
            fg=get_color("fg_primary"),
            bg=get_color("header_bg"),
        )
        title.pack(side=tk.LEFT, padx=UI_CONFIG["padding_lg"], pady=UI_CONFIG["padding_md"])

        # Status indicator
        self.status_indicator = tk.Label(
            header,
            text=get_icon("sleep"),
            font=("Arial", 16),
            fg=get_color("warning"),
            bg=get_color("header_bg"),
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=UI_CONFIG["padding_md"], pady=UI_CONFIG["padding_md"])

        # Status text
        self.status_text = tk.Label(
            header,
            text="Sleeping",
            font=get_font("normal"),
            fg=get_color("fg_secondary"),
            bg=get_color("header_bg"),
        )
        self.status_text.pack(side=tk.RIGHT, padx=(0, 10), pady=UI_CONFIG["padding_md"])

    def _build_main_content(self):
        """Build main content area (left and right panels)"""
        main_frame = tk.Frame(self.root, bg=get_color("bg_primary"))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=UI_CONFIG["padding_md"], pady=UI_CONFIG["padding_md"])

        # Left panel: Control & Commands
        left_panel = tk.Frame(main_frame, bg=get_color("bg_primary"))
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, UI_CONFIG["padding_sm"]))

        self._build_control_panel(left_panel)  # Implemented by subclasses
        self._build_command_section(left_panel)

        # Right panel: Output
        right_panel = tk.Frame(main_frame, bg=get_color("bg_primary"))
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(UI_CONFIG["padding_sm"], 0))

        self._build_output_section(right_panel)

    def _build_control_panel(self, parent):
        """
        Build control panel (must be implemented by subclasses)
        
        Args:
            parent: Parent frame
        """
        raise NotImplementedError("Subclasses must implement _build_control_panel()")

    def _build_command_section(self, parent):
        """Build command input section"""
        # Header
        section_header = tk.Label(
            parent,
            text="💬 Send Command",
            font=get_font("heading"),
            fg=get_color("accent"),
            bg=get_color("bg_primary"),
        )
        section_header.pack(anchor="w", pady=(UI_CONFIG["padding_md"], UI_CONFIG["padding_sm"]))

        # Command frame
        cmd_frame = tk.Frame(
            parent,
            bg=get_color("bg_secondary"),
            relief=tk.SUNKEN,
            bd=1
        )
        cmd_frame.pack(fill=tk.BOTH, expand=True, pady=(0, UI_CONFIG["padding_md"]))

        # Input label
        tk.Label(
            cmd_frame,
            text="Enter command:",
            font=get_font("small"),
            fg=get_color("fg_primary"),
            bg=get_color("bg_secondary"),
        ).pack(anchor="w", padx=UI_CONFIG["padding_md"], pady=(UI_CONFIG["padding_md"], UI_CONFIG["padding_sm"]))

        # Input field
        self.command_input = tk.Entry(
            cmd_frame,
            font=get_font("normal"),
            bg=get_color("bg_tertiary"),
            fg=get_color("fg_primary"),
            insertbackground=get_color("fg_primary"),
        )
        self.command_input.pack(fill=tk.X, padx=UI_CONFIG["padding_md"], pady=(0, UI_CONFIG["padding_sm"]))
        self.command_input.bind("<Return>", lambda e: self._on_send_command())

        # Send button
        btn_send = tk.Button(
            cmd_frame,
            text=f"{get_icon('send')} Send Command",
            command=self._on_send_command,
            bg=get_color("accent"),
            fg="#000000",
            font=get_font("normal"),
            padx=UI_CONFIG["padding_md"],
            pady=UI_CONFIG["padding_sm"],
        )
        btn_send.pack(fill=tk.X, padx=UI_CONFIG["padding_md"], pady=(0, UI_CONFIG["padding_md"]))

        # Quick commands header
        tk.Label(
            cmd_frame,
            text="Quick Commands:",
            font=get_font("subheading"),
            fg=get_color("accent"),
            bg=get_color("bg_secondary"),
        ).pack(anchor="w", padx=UI_CONFIG["padding_md"], pady=(UI_CONFIG["padding_md"], UI_CONFIG["padding_sm"]))

        # Quick command buttons
        quick_frame = tk.Frame(cmd_frame, bg=get_color("bg_secondary"))
        quick_frame.pack(fill=tk.X, padx=UI_CONFIG["padding_md"], pady=(0, UI_CONFIG["padding_md"]))

        for label, command in self._get_quick_commands():
            btn = tk.Button(
                quick_frame,
                text=label,
                command=lambda cmd=command: self._send_command_direct(cmd),
                bg=get_color("bg_tertiary"),
                fg=get_color("fg_primary"),
                font=get_font("small"),
                padx=UI_CONFIG["padding_sm"],
                pady=UI_CONFIG["padding_xs"],
            )
            btn.pack(side=tk.LEFT, padx=UI_CONFIG["padding_xs"], pady=UI_CONFIG["padding_xs"])

    def _build_output_section(self, parent):
        """Build output console section"""
        section_header = tk.Label(
            parent,
            text=f"{get_icon('console')} Output & Results",
            font=get_font("heading"),
            fg=get_color("accent"),
            bg=get_color("bg_primary"),
        )
        section_header.pack(anchor="w", pady=(0, UI_CONFIG["padding_md"]))

        # Console
        self.console = scrolledtext.ScrolledText(
            parent,
            bg=get_color("console_bg"),
            fg=get_color("console_fg"),
            font=get_font("console"),
            wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        # Configure color tags
        self.console.tag_configure("info", foreground=get_color("info"))
        self.console.tag_configure("success", foreground=get_color("success"))
        self.console.tag_configure("warning", foreground=get_color("warning"))
        self.console.tag_configure("error", foreground=get_color("error"))

    def _build_footer(self):
        """Build bottom footer"""
        footer = tk.Frame(
            self.root,
            bg=get_color("bg_secondary"),
            height=50
        )
        footer.pack(fill=tk.X, pady=0)

        # Status text
        tk.Label(
            footer,
            text="Voice Assistant Ready",
            font=get_font("small"),
            fg=get_color("fg_secondary"),
            bg=get_color("bg_secondary"),
        ).pack(side=tk.LEFT, padx=UI_CONFIG["padding_lg"], pady=UI_CONFIG["padding_sm"])

        # Exit button
        exit_btn = tk.Button(
            footer,
            text=f"{get_icon('exit')} Exit",
            command=self._on_exit,
            bg=get_color("error"),
            fg=get_color("fg_primary"),
            font=get_font("normal"),
            padx=UI_CONFIG["padding_md"],
            pady=UI_CONFIG["padding_xs"],
        )
        exit_btn.pack(side=tk.RIGHT, padx=UI_CONFIG["padding_lg"], pady=UI_CONFIG["padding_sm"])

    # ─────────────────────────────────────────────────────────────────────────
    # Methods to be implemented by subclasses
    # ─────────────────────────────────────────────────────────────────────────

    def _get_quick_commands(self) -> list:
        """
        Get quick command buttons
        Should return list of (label, command) tuples
        
        Returns:
            list: [(label, command), ...]
        """
        raise NotImplementedError("Subclasses must implement _get_quick_commands()")

    # ─────────────────────────────────────────────────────────────────────────
    # Common Button Handlers
    # ─────────────────────────────────────────────────────────────────────────

    def _on_send_command(self):
        """Handle send button click"""
        command = self.command_input.get().strip()
        if command:
            self._send_command_direct(command)
            self.command_input.delete(0, tk.END)

    def _send_command_direct(self, command: str):
        """Send command to assistant (must be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement _send_command_direct()")

    def _on_exit(self):
        """Handle exit button"""
        if messagebox.askyesno("Exit", "Close the assistant?"):
            if self.assistant:
                self.assistant.running = False
            self.root.quit()

    def _update_status_awake(self):
        """Update status to show assistant is awake"""
        self.status_indicator.config(text=get_icon("awake"), fg=get_color("success"))
        self.status_text.config(text="Awake", fg=get_color("success"))

    def _update_status_sleeping(self):
        """Update status to show assistant is sleeping"""
        self.status_indicator.config(text=get_icon("sleep"), fg=get_color("warning"))
        self.status_text.config(text="Sleeping", fg=get_color("warning"))

    # ─────────────────────────────────────────────────────────────────────────
    # Console & Logging
    # ─────────────────────────────────────────────────────────────────────────

    def log_console(self, message: str, level: str = "info"):
        """
        Log message to console with color
        
        Args:
            message: Message to log
            level: "info", "success", "warning", "error"
        """
        tag = level if level in ["info", "success", "warning", "error"] else "info"
        self.console.insert(tk.END, f"{message}\n", tag)
        self.console.see(tk.END)
        self.root.update()

    def log_message(self, message: str, level: str = "info"):
        """
        Log message to console (alias for log_console)
        
        Args:
            message: Message to log
            level: "info", "success", "warning", "error"
        """
        self.log_console(message, level)

    # ─────────────────────────────────────────────────────────────────────────
    # Window Control
    # ─────────────────────────────────────────────────────────────────────────

    def show(self):
        """Show GUI window"""
        self.root.deiconify()
        self.log_console("✓ GUI initialized", "success")

    def run(self):
        """Start the GUI event loop"""
        self.root.mainloop()

    def close(self):
        """Close GUI gracefully"""
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error closing GUI: {e}")
