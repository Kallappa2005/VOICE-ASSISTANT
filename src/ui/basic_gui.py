"""
Basic Assistant GUI
GUI for main.py - Basic Voice Commands
Wake/Sleep, Navigation, YouTube, Screenshots, etc.
"""

import tkinter as tk
from threading import Thread

from src.core.logger import setup_logger
from .base_gui import BaseAssistantGUI
from .styles import get_icon, QUICK_COMMANDS

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
            text="🎮 Control Panel",
            font=("Arial", 12, "bold"),
            fg="#4CAF50",
            bg="#1a1a1a",
        )
        section_header.pack(anchor="w", pady=(0, 10))

        # Control frame
        ctrl_frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.SUNKEN, bd=1)
        ctrl_frame.pack(fill=tk.X, pady=(0, 15))

        # Wake button
        self.btn_wake = tk.Button(
            ctrl_frame,
            text=f"{get_icon('wake')} Wake Up",
            command=self._on_wake,
            bg="#00FF00",
            fg="#000000",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=12,
        )
        self.btn_wake.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Sleep button
        self.btn_sleep = tk.Button(
            ctrl_frame,
            text=f"{get_icon('sleep_action')} Sleep",
            command=self._on_sleep,
            bg="#FFA500",
            fg="#000000",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=12,
            state=tk.DISABLED,
        )
        self.btn_sleep.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Status label
        tk.Label(
            ctrl_frame,
            text="Status:",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#2d2d2d",
        ).pack(anchor="w", padx=10, pady=(10, 0))

        self.current_status = tk.Label(
            ctrl_frame,
            text="🔴 Sleeping",
            font=("Arial", 10),
            fg="#FFA500",
            bg="#2d2d2d",
        )
        self.current_status.pack(anchor="w", padx=20, pady=(0, 10))

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
            self.current_status.config(text="🟢 Awake", fg="#00FF00")
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
            self.current_status.config(text="🔴 Sleeping", fg="#FFA500")
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

        if not self.assistant.is_awake:
            self.log_console("⚠️ Assistant is sleeping. Wake up first!", "warning")
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
