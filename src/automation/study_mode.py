"""
Study Mode Module
=================
Launches a focused study environment from the 'study_mode' block in config.json:

  1. Mutes system notifications via Focus Assist (Windows) or a placeholder
  2. Opens YouTube in the default browser, searching for the requested topic
  3. Opens the documentation URL (default: GeeksforGeeks)
  4. Opens Notepad for note-taking

Triggered by voice command: "study mode" / "start studying" / "focus mode"

Optional topic argument:
    StudyMode().start_study_mode(topic="React hooks")
    StudyMode().start_study_mode()          # uses default topic from config
"""

import json
import os
import subprocess
import time
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

from src.core.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Default fallback values (used when keys are missing from config.json)
# ---------------------------------------------------------------------------
_DEFAULT_YOUTUBE_URL = "https://www.youtube.com/results?search_query={topic}"
_DEFAULT_DOCS_URL    = "https://www.geeksforgeeks.org"
_DEFAULT_NOTEPAD_CMD = "notepad.exe"
_DEFAULT_TOPIC       = "programming tutorial"


class StudyMode:
    """Manages the 'Study Mode' voice-assistant workflow."""

    # config.json lives at the project root:
    # src/automation/study_mode.py → src/automation → src → project_root
    DEFAULT_CONFIG_PATH = (
        Path(__file__).resolve().parent.parent.parent / "config.json"
    )

    def __init__(self, config_path=None):
        """
        Initialise StudyMode.

        Args:
            config_path (str | Path | None): Override config location.
                Defaults to <project_root>/config.json.
        """
        self.config_path = (
            Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        )
        logger.info(f"StudyMode initialised (config: {self.config_path})")

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def start_study_mode(self, topic: str = None):
        """
        Run the full study-mode setup sequence.

        Steps
        -----
        1. Load & validate config.json
        2. Mute system notifications (Focus Assist / placeholder)
        3. Open YouTube with the given/default topic
        4. Open the documentation URL (e.g., GeeksforGeeks)
        5. Open Notepad for note-taking

        Args:
            topic (str | None): Study topic (e.g. "React hooks").
                If None or empty, falls back to config's default_topic
                or the built-in default "programming tutorial".

        Returns
        -------
        dict
            {
                'success': bool,
                'error':   str | None,
                'steps':   list[str]   # human-readable log of every step
            }
        """
        steps = []

        # ── Banner ────────────────────────────────────────────────────────
        print("\n" + "=" * 65)
        print("📚  STARTING STUDY MODE")
        print("=" * 65)

        # ── Step 1 : Load config ──────────────────────────────────────────
        config, error = self._load_config()
        if error:
            msg = f"❌  Config error: {error}"
            print(msg)
            logger.error(msg)
            return {"success": False, "error": error, "steps": [msg]}

        cfg = config.get("study_mode", {})

        # Resolve values (config → built-in defaults)
        youtube_url_template = cfg.get("youtube_url", _DEFAULT_YOUTUBE_URL).strip()
        docs_url             = cfg.get("docs_url",    _DEFAULT_DOCS_URL).strip()
        notepad_cmd          = cfg.get("notepad_command", _DEFAULT_NOTEPAD_CMD).strip()
        mute_cmd             = cfg.get("mute_notifications_command", "focus_assist_on").strip()
        config_default_topic = cfg.get("default_topic", _DEFAULT_TOPIC).strip()

        # Resolve topic: argument > config default > built-in default
        resolved_topic = (topic or "").strip() or config_default_topic or _DEFAULT_TOPIC

        # Build the final YouTube URL
        youtube_url = youtube_url_template.replace(
            "{topic}", quote_plus(resolved_topic)
        )

        # Pretty-print resolved config
        print(f"   📖  Topic    : {resolved_topic}")
        print(f"   📺  YouTube  : {youtube_url}")
        print(f"   📄  Docs URL : {docs_url or '(not set)'}")
        print(f"   📝  Notepad  : {notepad_cmd or '(not set)'}")
        print(f"   🔕  Mute cmd : {mute_cmd or '(not set)'}")
        print()

        # ── Step 2 : Mute notifications ───────────────────────────────────
        print("🔧  Step 1/4  →  Muting system notifications...")
        step = self._mute_notifications(mute_cmd)
        steps.append(step)
        print(f"   {step}")
        time.sleep(0.5)

        # ── Step 3 : Open YouTube ─────────────────────────────────────────
        print("🔧  Step 2/4  →  Opening YouTube...")
        step = self._open_url(youtube_url, label=f"YouTube ({resolved_topic})")
        steps.append(step)
        print(f"   {step}")
        time.sleep(1.0)       # stagger browser tabs

        # ── Step 4 : Open documentation URL ──────────────────────────────
        if docs_url:
            print("🔧  Step 3/4  →  Opening documentation...")
            step = self._open_url(docs_url, label="Docs (GeeksforGeeks)")
            steps.append(step)
            print(f"   {step}")
            time.sleep(0.8)
        else:
            msg = "⚠️  docs_url not configured — skipped"
            steps.append(msg)
            print(f"   {msg}")

        # ── Step 5 : Open Notepad ─────────────────────────────────────────
        if notepad_cmd:
            print("🔧  Step 4/4  →  Opening Notepad...")
            step = self._open_notepad(notepad_cmd)
            steps.append(step)
            print(f"   {step}")
        else:
            msg = "⚠️  notepad_command not configured — skipped"
            steps.append(msg)
            print(f"   {msg}")

        # ── Done ──────────────────────────────────────────────────────────
        print()
        print("✅  Study Mode is ready! Good luck studying.")
        print("=" * 65)
        logger.info(f"Study Mode launched (topic: {resolved_topic})")
        return {"success": True, "error": None, "steps": steps}

    def validate_config(self):
        """
        Validate the study_mode block in config.json and print a report.

        Returns
        -------
        bool
            True if config is readable and has a study_mode block.
        """
        config, error = self._load_config()
        if error:
            print(f"[ERROR]  {error}")
            return False

        cfg = config.get("study_mode", {})

        print("\n[CONFIG VALIDATION — study_mode]")
        print("-" * 50)
        for key in ("youtube_url", "docs_url", "notepad_command",
                    "mute_notifications_command", "default_topic"):
            val = cfg.get(key, "")
            status = "OK" if val else "(not configured — will use built-in default)"
            print(f"  {key:<34s} : {val if val else status}")
        print("-" * 50)
        return True

    # ──────────────────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────────────────

    def _load_config(self):
        """
        Read and parse config.json.

        Returns
        -------
        tuple(dict, str | None)
            (config_dict, error_message) — error_message is None on success.
        """
        if not self.config_path.exists():
            return {}, (
                f"config.json not found at: {self.config_path}\n"
                "  Please create it at the project root."
            )
        try:
            with open(self.config_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            logger.info(f"config.json loaded from: {self.config_path}")
            return data, None
        except json.JSONDecodeError as exc:
            return {}, f"Invalid JSON in config.json — {exc}"
        except PermissionError:
            return {}, f"Permission denied reading config.json: {self.config_path}"
        except Exception as exc:
            return {}, f"Could not read config.json: {exc}"

    def _mute_notifications(self, mute_cmd: str):
        """
        Attempt to enable Focus Assist (quiet hours) on Windows to suppress
        notifications during study sessions.

        Strategy
        --------
        - If mute_cmd == "focus_assist_on" → use the PowerShell registry trick
          to enable Focus Assist (Alarms-only / priority-only mode).
        - Any other non-empty string → treat as a raw shell command and run it.
        - Empty / None → skip with a warning.

        Returns
        -------
        str: Human-readable step result.
        """
        if not mute_cmd:
            return "⚠️  No mute command configured — notifications not muted"

        # ── Built-in Focus Assist via registry ────────────────────────────
        if mute_cmd.lower() == "focus_assist_on":
            return self._enable_focus_assist()

        # ── Custom shell command ───────────────────────────────────────────
        return self._run_shell_command(mute_cmd, label="Mute notifications")

    def _enable_focus_assist(self):
        """
        Enable Windows Focus Assist (Quiet Hours) by writing to the registry.

        Focus Assist values:
            0 = Off
            1 = Priority only
            2 = Alarms only

        We set it to 2 (Alarms only = maximum focus).

        Returns
        -------
        str: Human-readable result.
        """
        try:
            # PowerShell one-liner: write WNF_SHEL_QUIETHOURS_ACTIVE_PROFILE_CHANGED
            ps_script = (
                "Set-ItemProperty -Path "
                "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' "
                "-Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Value 0 -Type DWord -Force; "
                "Write-Output 'Focus Assist enabled'"
            )
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info("Focus Assist enabled via registry")
                return "✅  Notifications muted (Focus Assist ON)"
            else:
                # Non-fatal — log and continue
                logger.warning(
                    f"Focus Assist registry write returned {result.returncode}: "
                    f"{result.stderr.strip()}"
                )
                return (
                    "⚠️  Could not enable Focus Assist automatically "
                    "(requires admin or unsupported Windows edition). "
                    "Please mute notifications manually."
                )
        except FileNotFoundError:
            logger.warning("powershell.exe not found — cannot mute notifications")
            return "⚠️  PowerShell not found — notifications not muted"
        except subprocess.TimeoutExpired:
            logger.warning("Focus Assist command timed out")
            return "⚠️  Mute command timed out — notifications not muted"
        except Exception as exc:
            logger.error(f"Focus Assist error: {exc}")
            return f"⚠️  Could not mute notifications: {exc}"

    def _run_shell_command(self, command: str, label: str = "Command"):
        """
        Run an arbitrary shell command (non-blocking).

        Args:
            command (str): Shell command string.
            label   (str): Human-readable name for logging.

        Returns
        -------
        str: Human-readable result.
        """
        try:
            subprocess.Popen(command, shell=True)
            logger.info(f"{label} executed: {command}")
            return f"✅  {label} → '{command}'"
        except Exception as exc:
            msg = f"❌  {label} failed: {exc}"
            logger.error(msg)
            return msg

    def _open_url(self, url: str, label: str = "URL"):
        """
        Open a URL in the system's default web browser (new tab).

        Args:
            url   (str): URL to open.
            label (str): Human-readable name for logging.

        Returns
        -------
        str: Human-readable result.
        """
        try:
            webbrowser.open(url, new=2)   # new=2 → prefer a new tab
            logger.info(f"Browser opened [{label}]: {url}")
            return f"✅  Browser → {label}"
        except Exception as exc:
            msg = f"❌  Failed to open {label} '{url}': {exc}"
            logger.error(msg)
            return msg

    def _open_notepad(self, notepad_cmd: str):
        """
        Launch Notepad (or any configured text editor).

        Args:
            notepad_cmd (str): Executable name or full path (e.g. 'notepad.exe').

        Returns
        -------
        str: Human-readable result.
        """
        try:
            subprocess.Popen(
                notepad_cmd,
                shell=True,                 # shell=True handles plain 'notepad.exe'
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Notepad launched: {notepad_cmd}")
            return f"✅  Notepad opened  → ready for notes"
        except FileNotFoundError:
            msg = f"❌  Notepad not found: '{notepad_cmd}'"
            logger.error(msg)
            return msg
        except Exception as exc:
            msg = f"❌  Failed to open Notepad: {exc}"
            logger.error(msg)
            return msg
