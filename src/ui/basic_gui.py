"""
Basic Assistant GUI
GUI for main.py - Basic Voice Commands
Wake/Sleep, Navigation, YouTube, Screenshots, etc.
"""

import tkinter as tk
from threading import Thread

from src.core.logger import setup_logger
from .base_gui import BaseAssistantGUI
from .styles import get_icon, QUICK_COMMANDS, get_color, get_font

logger = setup_logger(__name__)


class BasicAssistantGUI(BaseAssistantGUI):
    """
    GUI for Basic Voice Assistant (main.py)
    
    Features:
    - Wake/Sleep control
    - Navigation commands
    - YouTube controls
    - Screenshot commands
    - General voice commands
    """

    def __init__(self, assistant=None):
        """Initialize Basic Assistant GUI"""
        super().__init__(assistant=assistant, mode="basic")
        logger.info("BasicAssistantGUI initialized")

    def _build_control_panel(self, parent):
        """Build control panel for basic assistant"""
        # Header
        section_header = tk.Label(
            parent,
            text="🎮 Control Center",
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
        ).pack(anchor="w", pady=(8, 0))

        self.current_status = tk.Label(
            inner,
            text="🔴 Sleeping",
            font=get_font("normal"),
            fg=get_color("warning"),
            bg=get_color("bg_tertiary"),
        )
        self.current_status.pack(anchor="w", pady=(0, 0))

    def _get_quick_commands(self) -> list:
        """Get quick command buttons for basic assistant"""
        return QUICK_COMMANDS.get("basic", [])

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
            self.log_console("✓ Assistant woke up!", "success")

            # Speak greeting
            if hasattr(self.assistant, 'tts'):
                Thread(
                    target=lambda: self.assistant.tts.speak(
                        "Hello! I'm ready. You can now give me commands."
                    ),
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
            self.log_console("😴 Assistant going to sleep", "warning")

            # Speak message
            if hasattr(self.assistant, 'tts'):
                Thread(
                    target=lambda: self.assistant.tts.speak(
                        "Going to sleep. Say wake up to wake me."
                    ),
                    daemon=True
                ).start()

        except Exception as e:
            self.log_console(f"❌ Error going to sleep: {e}", "error")
            logger.error(f"Sleep error: {e}", exc_info=True)

    def _send_command_direct(self, command: str):
        """Send command to basic assistant"""
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
                self.assistant.handle_command(intent, params)

            except Exception as e:
                self.log_console(f"❌ Error: {e}", "error")
                logger.error(f"Command error: {e}", exc_info=True)

        thread = Thread(target=process, daemon=True)
        thread.start()
