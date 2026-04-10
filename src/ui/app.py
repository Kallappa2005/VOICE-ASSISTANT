"""
Agent UI
========
Lightweight tkinter window that exposes the full Voice Assistant agent
pipeline through both typed text and microphone voice input.

Run standalone:
    python src/ui/app.py

Or import and embed:
    from src.ui.app import AgentUI
    AgentUI().run()

Pipeline (per command)
----------------------
    input (text / voice)
        -> CommandParser  (intent detection)
        -> IntentEnhancer (is this a developer task?)
        -> TaskPlanner    (generate step list)
        -> show plan in console
        -> confirm via popup dialog
        -> ExecutionManager (run steps, mirror output to console)
        -> TTS: "Your project is ready and running"
"""

import sys
import os
import threading

import tkinter as tk
from tkinter import messagebox

# Ensure project root is on path when run as __main__
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.logger import setup_logger
from src.commands.command_parser import CommandParser
from src.agent.intent_enhancer import IntentEnhancer
from src.agent.task_planner import TaskPlanner
from src.agent.execution_manager import ExecutionManager
from src.ui.components import (
    COLORS,
    make_input_field,
    make_button,
    make_output_console,
    make_separator,
)

logger = setup_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# stdout redirector (thread-safe: uses root.after for UI writes)
# ─────────────────────────────────────────────────────────────────────────────

class _UIWriter:
    """Redirect Python print() output to the AgentUI console."""

    def __init__(self, ui: 'AgentUI'):
        self.ui = ui

    def write(self, text: str):
        if text and text.strip():
            # root.after is thread-safe in tkinter
            snippet = text.rstrip()
            self.ui.root.after(0, lambda s=snippet: self.ui.log("  " + s))

    def flush(self):
        pass   # required by the file protocol


# ─────────────────────────────────────────────────────────────────────────────
# Main UI class
# ─────────────────────────────────────────────────────────────────────────────

class AgentUI:
    """
    Tkinter-based GUI for the Voice Assistant Agent system.

    Features
    --------
    - Dark-themed window (900 x 660 px)
    - Scrollable output console (mirrors stdout during execution)
    - Text input field (press Enter or click Send)
    - Voice input button (SpeechRecognitionHandler in background thread)
    - Confirmation popup for developer task plans
    - TTS voice feedback on project completion
    """

    # ── Init ─────────────────────────────────────────────────────────────────

    def __init__(self):
        logger.info("AgentUI initialising")

        # Core pipeline components
        self.parser   = CommandParser()
        self.enhancer = IntentEnhancer()
        self.planner  = TaskPlanner()

        # TTS (optional — graceful fallback if unavailable)
        self.tts = None
        try:
            from src.speech.text_to_speech_handler import TextToSpeechHandler
            self.tts = TextToSpeechHandler(rate=160)
            logger.info("TTS available")
        except Exception as exc:
            logger.warning(f"TTS unavailable: {exc}")

        # Execution manager (receives tts for post-execution voice)
        self.execution_manager = ExecutionManager(tts=self.tts,
                                                  planner=self.planner)

        # STT — lazy: only initialised when voice button is first pressed
        self.stt = None

        # Default project output directory (user's home)
        self.project_dir = str(os.path.expanduser("~"))

        # State
        self._voice_active = False

        # Build Tk root
        self.root = tk.Tk()
        self._build_ui()
        logger.info("AgentUI initialised")

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        """Assemble all tkinter widgets."""
        root = self.root
        root.title("AI Voice Assistant — Agent Mode")
        root.configure(bg=COLORS['bg'])
        root.geometry("920x680")
        root.resizable(True, True)
        root.minsize(700, 500)

        # ── Title bar ─────────────────────────────────────────────────────────
        header = tk.Frame(root, bg=COLORS['bg'], pady=12)
        header.pack(fill='x', padx=20)

        tk.Label(
            header,
            text="AI Voice Assistant",
            font=('Consolas', 18, 'bold'),
            fg=COLORS['primary'],
            bg=COLORS['bg'],
        ).pack(side='left')

        tk.Label(
            header,
            text="Agent Mode  |  Developer Automation",
            font=('Consolas', 10),
            fg=COLORS['text_dim'],
            bg=COLORS['bg'],
        ).pack(side='right', padx=4)

        make_separator(root).pack(fill='x', padx=20)

        # ── Info bar (project dir) ─────────────────────────────────────────────
        info_bar = tk.Frame(root, bg=COLORS['surface'], pady=4)
        info_bar.pack(fill='x', padx=20, pady=(6, 0))

        tk.Label(
            info_bar,
            text="Output dir:",
            font=('Consolas', 9),
            fg=COLORS['text_dim'],
            bg=COLORS['surface'],
        ).pack(side='left', padx=(8, 4))

        self._dir_var = tk.StringVar(value=self.project_dir)
        tk.Label(
            info_bar,
            textvariable=self._dir_var,
            font=('Consolas', 9),
            fg=COLORS['text'],
            bg=COLORS['surface'],
        ).pack(side='left')

        make_button(
            info_bar, 'Change', self._pick_dir,
            color=COLORS['border'], padx=8, pady=2,
        ).pack(side='right', padx=6)

        # ── Output console ────────────────────────────────────────────────────
        console_frame = tk.Frame(root, bg=COLORS['bg'])
        console_frame.pack(fill='both', expand=True, padx=20, pady=8)

        self.console = make_output_console(console_frame, height=26)
        self.console.pack(fill='both', expand=True)

        # ── Input row ─────────────────────────────────────────────────────────
        input_row = tk.Frame(root, bg=COLORS['bg'], pady=8)
        input_row.pack(fill='x', padx=20)

        self.input_field = make_input_field(input_row)
        self.input_field.pack(side='left', fill='x', expand=True, padx=(0, 8))
        self.input_field.bind('<Return>', lambda _e: self._on_send())
        self.input_field.focus_set()

        self.send_btn = make_button(
            input_row, 'Send', self._on_send, COLORS['primary']
        )
        self.send_btn.pack(side='left', padx=(0, 8))

        self.voice_btn = make_button(
            input_row, '[MIC] Voice', self._on_voice, COLORS['success']
        )
        self.voice_btn.pack(side='left')

        # ── Status bar ────────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="Ready  |  Type a command or click [MIC] Voice")
        tk.Label(
            root,
            textvariable=self._status_var,
            font=('Consolas', 9),
            fg=COLORS['text_dim'],
            bg='#111827',
            anchor='w',
            padx=12,
            pady=4,
        ).pack(fill='x', side='bottom')

        # ── Welcome message ────────────────────────────────────────────────────
        self._welcome()

    def _welcome(self):
        """Print the startup guide to the console."""
        lines = [
            "=" * 62,
            "  AI Voice Assistant  -  Agent Mode",
            "=" * 62,
            "",
            "  Developer Commands (agent pipeline):",
            "    build react project            -> React + Vite scaffold",
            "    build react project my-app     -> Named React app",
            "    create node app with express   -> Node.js + Express",
            "    create node app my-api         -> Named Node project",
            "",
            "  UI Commands:",
            "    help   -> Show this guide",
            "    clear  -> Clear the console",
            "",
            "  Note: For browser / YouTube / scroll commands",
            "        run  python main_ai.py  instead.",
            "=" * 62,
            "",
        ]
        for line in lines:
            self.log(line)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_send(self):
        """Handle Send button / Enter key."""
        text = self.input_field.get().strip()
        if not text:
            return
        self.input_field.delete(0, 'end')
        self.log(f"\n> {text}")
        threading.Thread(
            target=self._process_command,
            args=(text,),
            daemon=True,
        ).start()

    def _on_voice(self):
        """Start voice capture in a background thread."""
        if self._voice_active:
            return
        self._voice_active = True
        self.voice_btn.config(state='disabled', text='Listening...')
        self._set_status("Listening...")
        threading.Thread(target=self._do_voice_input, daemon=True).start()

    def _do_voice_input(self):
        """Background: capture microphone input, then dispatch."""
        try:
            if self.stt is None:
                from src.speech.speech_recognition_handler import SpeechRecognitionHandler
                self.root.after(0, lambda: self.log("  [MIC] Calibrating microphone..."))
                self.stt = SpeechRecognitionHandler()
                self.stt.calibrate(duration=1.0)

            self.root.after(0, lambda: self.log("  [MIC] Speak now..."))
            command = self.stt.listen()

            if command:
                self.root.after(0, lambda c=command: self.log(f"\n[VOICE] > {c}"))
                # Start processing in its own thread (avoids blocking voice thread)
                threading.Thread(
                    target=self._process_command,
                    args=(command,),
                    daemon=True,
                ).start()
            else:
                self.root.after(0, lambda: self.log(
                    "  [WARN] No audio detected. Try speaking closer to the mic."
                ))
        except Exception as exc:
            logger.error(f"Voice input error: {exc}")
            self.root.after(0, lambda e=exc: self.log(f"  [ERR] Voice error: {e}"))
        finally:
            self.root.after(0, self._reset_voice_btn)

    def _reset_voice_btn(self):
        self.voice_btn.config(state='normal', text='[MIC] Voice')
        self._voice_active = False
        self._set_status("Ready")

    # ── Command pipeline ──────────────────────────────────────────────────────

    def _process_command(self, text: str):
        """
        Full command pipeline — always runs in a background thread.
        UI updates use self.root.after() for thread safety.
        """
        try:
            self.root.after(0, lambda: self._set_status(
                f"Processing: {text[:45]}..."
            ))
            text_stripped = text.strip()
            text_lower    = text_stripped.lower()

            # ── Special UI-only commands ──────────────────────────────────────
            if text_lower in ('clear', 'cls'):
                self.root.after(0, self._clear_console)
                self.root.after(0, lambda: self._set_status("Ready"))
                return

            if text_lower in ('help', 'h', '?'):
                self.root.after(0, self._show_help)
                self.root.after(0, lambda: self._set_status("Ready"))
                return

            # ── Developer task? ───────────────────────────────────────────────
            if self.enhancer.is_developer_task(text_stripped):
                self._handle_developer_task(text_stripped)
            else:
                # Non-developer: show intent (browser commands need main_ai.py)
                parsed = self.parser.parse(text_stripped)
                intent = parsed.get('intent', 'unknown')
                self.root.after(0, lambda i=intent: self.log(
                    f"  [INFO] Detected intent: {i}\n"
                    "  [INFO] For browser/YouTube/scroll commands use:\n"
                    "         python main_ai.py"
                ))

        except Exception as exc:
            logger.error(f"_process_command error: {exc}", exc_info=True)
            self.root.after(0, lambda e=exc: self.log(f"\n  [ERR] Unexpected error: {e}"))
        finally:
            self.root.after(0, lambda: self._set_status("Ready"))

    def _handle_developer_task(self, text: str):
        """Full agent pipeline for a developer task (runs in background thread)."""
        try:
            # 1. Enhance intent
            self.root.after(0, lambda: self.log("\n  [AGENT] Analyzing command..."))
            enhanced  = self.enhancer.enhance(text)
            goal      = enhanced.get('goal', 'unknown')
            proj_name = enhanced.get('name') or '(auto-generated)'
            framework = enhanced.get('framework')

            self.root.after(0, lambda: self.log(
                f"  [AGENT] Goal      : {goal}\n"
                f"  [AGENT] Project   : {proj_name}"
                + (f"\n  [AGENT] Framework : {framework}" if framework else "")
            ))

            # 2. Generate plan
            steps = self.planner.plan(enhanced)
            if not steps:
                self.root.after(0, lambda: self.log(
                    "  [WARN] Could not generate a plan for this command."
                ))
                return

            # 3. Display plan
            plan_header = (
                "\n  " + "=" * 58 + "\n"
                "  [PLAN]  EXECUTION PLAN\n"
                "  " + "=" * 58 + "\n"
                "  I will perform these steps:\n"
            )
            plan_body = "\n".join(
                f"    {line}"
                for line in self.planner.describe_plan(steps).splitlines()
            )
            plan_footer = "\n  " + "=" * 58
            full_plan   = plan_header + plan_body + plan_footer
            self.root.after(0, lambda p=full_plan: self.log(p))

            # 4. Confirmation dialog (must appear on main thread)
            confirmed = self._ask_confirm_dialog(goal, len(steps))
            if not confirmed:
                self.root.after(0, lambda: self.log(
                    "\n  [CANCEL]  Plan rejected — nothing was created.\n"
                ))
                return

            # 5. Execute (redirect stdout -> console)
            self.root.after(0, lambda: self.log(
                "\n  [RUN]  Starting execution...\n"
            ))
            self.root.after(0, lambda: self._set_status("Executing..."))

            original_stdout = sys.stdout
            sys.stdout = _UIWriter(self)
            try:
                result = self.execution_manager.execute(
                    steps, project_dir=self.project_dir
                )
            finally:
                sys.stdout = original_stdout

            # 6. Result
            if result['success']:
                proj_path = result.get('project_path') or self.project_dir
                ok_msg = (
                    f"\n  [DONE]  All {result['total_steps']} steps completed!\n"
                    f"  [DIR]   Project created at: {proj_path}\n"
                )
                self.root.after(0, lambda m=ok_msg: self.log(m))
                if self.tts:
                    try:
                        self.tts.speak("Your project is ready and running.")
                    except Exception:
                        pass
            else:
                fail_msg = (
                    f"\n  [FAIL]  {result.get('error', 'Unknown error')}\n"
                    f"          {result['completed_steps']} / "
                    f"{result['total_steps']} steps completed.\n"
                )
                self.root.after(0, lambda m=fail_msg: self.log(m))

        except Exception as exc:
            logger.error(f"Developer task error: {exc}", exc_info=True)
            self.root.after(0, lambda e=exc: self.log(
                f"\n  [ERR] Agent pipeline error: {e}\n"
            ))

    # ── Confirmation dialog (thread-safe) ─────────────────────────────────────

    def _ask_confirm_dialog(self, goal: str, step_count: int) -> bool:
        """
        Show a Yes/No dialog.  Safe to call from a background thread.

        Uses threading.Event to block the caller until the user responds.
        The dialog itself is scheduled on the main (Tk event-loop) thread.
        """
        result  = {'value': False}
        barrier = threading.Event()

        def _show():
            answer = messagebox.askyesno(
                title="Confirm Execution",
                message=(
                    f"Goal: {goal.replace('_', ' ')}\n"
                    f"Steps: {step_count}\n\n"
                    "Do you want to continue?\n"
                    f"Projects will be created in:\n{self.project_dir}"
                ),
                parent=self.root,
            )
            result['value'] = bool(answer)
            barrier.set()

        self.root.after(0, _show)
        barrier.wait(timeout=120)   # give user 2 minutes to respond
        return result['value']

    # ── UI utilities ──────────────────────────────────────────────────────────

    def log(self, message: str):
        """Append a line to the output console (call from any thread via root.after)."""
        try:
            self.console.config(state='normal')
            self.console.insert('end', message + '\n')
            self.console.see('end')
            self.console.config(state='disabled')
        except tk.TclError:
            pass   # window may be closing

    def _set_status(self, message: str):
        try:
            self._status_var.set(message)
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def _clear_console(self):
        self.console.config(state='normal')
        self.console.delete('1.0', 'end')
        self.console.config(state='disabled')
        self.log("Console cleared. Type 'help' for commands.\n")

    def _show_help(self):
        lines = [
            "",
            "  " + "=" * 58,
            "  AVAILABLE COMMANDS",
            "  " + "=" * 58,
            "  Developer (Agent Pipeline):",
            "    build react project [name]",
            "    create react app [name]",
            "    new react project",
            "    create node app [name]",
            "    create node app with express",
            "    build node project [name]",
            "",
            "  UI Commands:",
            "    help   -> Show this guide",
            "    clear  -> Clear console",
            "",
            "  For browser/YouTube/AI commands:",
            "    run python main_ai.py in terminal",
            "  " + "=" * 58,
            "",
        ]
        for line in lines:
            self.log(line)

    def _pick_dir(self):
        """Open a directory chooser dialog to change the output path."""
        try:
            from tkinter import filedialog
            chosen = filedialog.askdirectory(
                title="Choose project output directory",
                initialdir=self.project_dir,
                parent=self.root,
            )
            if chosen:
                self.project_dir = chosen
                self._dir_var.set(chosen)
                self.log(f"  [DIR]  Output directory changed to: {chosen}")
        except Exception as exc:
            logger.error(f"Directory picker error: {exc}")

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self):
        """Start the Tk main event loop."""
        logger.info("AgentUI main loop started")
        self.root.mainloop()
        logger.info("AgentUI closed")


# ─────────────────────────────────────────────────────────────────────────────
# Standalone entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Run the GUI as a standalone application."""
    try:
        app = AgentUI()
        app.run()
    except KeyboardInterrupt:
        print("\nUI closed by user.")
    except Exception as exc:
        print(f"\n[ERR] UI startup error: {exc}")
        logger.error(f"UI startup error: {exc}", exc_info=True)


if __name__ == "__main__":
    main()
