"""
Coding Mode Module
==================
Launches a full development environment from config.json:
  1. Opens VS Code with the configured project folder
  2. Spawns a new visible terminal window and runs the configured command
  3. Opens the configured URLs in the default web browser

Triggered by voice command: "start coding" / "coding mode"
"""

import json
import os
import subprocess
import time
import webbrowser
from pathlib import Path

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class CodingMode:
    """Manages the 'Start Coding Mode' voice-assistant workflow."""

    # config.json lives at the project root — 3 levels up from this file:
    # src/automation/coding_mode.py → src/automation → src → project_root
    DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config.json"

    def __init__(self, config_path=None):
        """
        Initialise CodingMode.

        Args:
            config_path (str | Path | None): Override config location.
                Defaults to <project_root>/config.json.
        """
        self.config_path = (
            Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        )
        logger.info(f"CodingMode initialised (config: {self.config_path})")

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def start_coding_mode(self):
        """
        Run the full coding-mode setup sequence.

        Steps
        -----
        1. Load & validate config.json
        2. Open VS Code with the project folder
        3. Open a new terminal window and execute the terminal_command
        4. Open docs_url and github_url in the default browser

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
        print("💻  STARTING CODING MODE")
        print("=" * 65)

        # ── Step 1 : Load config ──────────────────────────────────────────
        config, error = self._load_config()
        if error:
            msg = f"❌  Config error: {error}"
            print(msg)
            logger.error(msg)
            return {"success": False, "error": error, "steps": [msg]}

        cfg             = config.get("start_coding", {})
        project_path    = cfg.get("project_path", "").strip()
        terminal_cmd    = cfg.get("terminal_command", "").strip()
        docs_url        = cfg.get("docs_url", "").strip()
        github_url      = cfg.get("github_url", "").strip()

        # Pretty-print loaded config
        print(f"   📂  Project  : {project_path or '(not set)'}")
        print(f"   🖥️   Command  : {terminal_cmd  or '(not set)'}")
        print(f"   📄  Docs URL : {docs_url       or '(not set)'}")
        print(f"   🐙  GitHub   : {github_url     or '(not set)'}")
        print()

        # Warn (don't abort) if project path is missing on disk
        if project_path and not os.path.isdir(project_path):
            warn = (
                f"⚠️  project_path does not exist on disk: {project_path}\n"
                "    VS Code will still be launched but may show an error."
            )
            print(warn)
            logger.warning(warn)

        # ── Step 2 : Open VS Code ─────────────────────────────────────────
        print("🔧  Step 1/3  →  Opening VS Code...")
        step = self._open_vscode(project_path)
        steps.append(step)
        print(f"   {step}")
        time.sleep(1.5)   # give VS Code time to start before terminal opens

        # ── Step 3 : Open terminal & run command ──────────────────────────
        if terminal_cmd:
            print("🔧  Step 2/3  →  Launching terminal...")
            step = self._run_in_new_terminal(project_path, terminal_cmd)
            steps.append(step)
            print(f"   {step}")
            time.sleep(1.0)
        else:
            steps.append("⚠️  terminal_command not configured — skipped")
            print("   ⚠️  terminal_command not configured — skipped")

        # ── Step 4 : Open URLs ────────────────────────────────────────────
        print("🔧  Step 3/3  →  Opening browser URLs...")
        for url in [docs_url, github_url]:
            if url:
                step = self._open_url(url)
                steps.append(step)
                print(f"   {step}")
                time.sleep(0.5)

        if not docs_url and not github_url:
            steps.append("⚠️  No URLs configured — skipped")
            print("   ⚠️  No URLs configured — skipped")

        # ── Done ──────────────────────────────────────────────────────────
        print()
        print("✅  Coding Mode is ready!")
        print("=" * 65)
        logger.info("Coding Mode launched successfully")
        return {"success": True, "error": None, "steps": steps}

    def validate_config(self):
        """
        Validate config.json and print a human-readable report.
        Useful for debugging before running start_coding_mode().

        Returns
        -------
        bool
            True if config.json is readable and contains a start_coding block.
        """
        config, error = self._load_config()
        if error:
            print(f"[ERROR]  {error}")
            return False

        cfg = config.get("start_coding", {})

        print("\n[CONFIG VALIDATION]")
        print("-" * 50)

        # project_path
        project_path = cfg.get("project_path", "")
        if project_path:
            exists = os.path.isdir(project_path)
            print(f"  project_path     : {project_path}")
            print(f"                     -> {'OK  (exists)' if exists else 'NOT FOUND on disk'}")
        else:
            print("  project_path     : (not configured)")

        # other string fields
        for key in ("terminal_command", "docs_url", "github_url"):
            val = cfg.get(key, "")
            status = "OK" if val else "(not configured)"
            print(f"  {key:<18s} : {val if val else status}")

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
            (config_dict, error_message)
            error_message is None on success.
        """
        if not self.config_path.exists():
            return {}, (
                f"config.json not found at: {self.config_path}\n"
                "  Please create it at the project root. "
                "See README or Commands.txt for the expected JSON format."
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

    def _open_vscode(self, project_path):
        """
        Launch VS Code.

        Tries the 'code' CLI command first (works when VS Code is on PATH),
        then falls back to the two most common Windows install locations.

        Args:
            project_path (str): Folder to open. Pass '' to open VS Code alone.

        Returns:
            str: Human-readable step result.
        """
        args_tail = [project_path] if project_path else []

        # 1st attempt — 'code' on PATH (most common after normal VS Code install)
        try:
            subprocess.Popen(
                ["code"] + args_tail,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"VS Code opened via 'code' CLI: {project_path or '(no path)'}")
            return f"✅  VS Code opened → {project_path or '(no project path)'}"

        except FileNotFoundError:
            pass  # 'code' not on PATH, try full exe paths below

        except Exception as exc:
            msg = f"❌  VS Code launch failed: {exc}"
            logger.error(msg)
            return msg

        # 2nd attempt — common Windows install paths
        username = os.getenv("USERNAME") or os.getenv("USER") or ""
        vscode_candidates = [
            rf"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
        ]

        for exe in vscode_candidates:
            if os.path.isfile(exe):
                try:
                    subprocess.Popen(
                        [exe] + args_tail,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    logger.info(f"VS Code opened via exe: {exe}")
                    return f"✅  VS Code opened → {project_path or '(no project path)'}"
                except Exception as exc:
                    logger.error(f"Failed to open VS Code via {exe}: {exc}")

        return (
            "⚠️  VS Code not found. "
            "Install it or ensure 'code' is added to your system PATH."
        )

    def _run_in_new_terminal(self, project_path, command):
        """
        Open a NEW visible PowerShell window, navigate to project_path,
        and run terminal_command.  The window stays open (-NoExit) so you
        can watch the output (e.g. nodemon logs).

        Why PowerShell instead of cmd?
        --------------------------------
        Passing ["cmd", "/K", "<cmd with quotes>"] through subprocess on
        Windows causes Python to escape the inner quotes, which breaks the
        cd path. PowerShell's Set-Location avoids this completely and is
        always available on Windows 11.

        Args:
            project_path (str): Directory to navigate to before running command.
            command (str): Shell command to execute (e.g. 'nodemon server.js').

        Returns:
            str: Human-readable step result.
        """
        try:
            if project_path and os.path.isdir(project_path):
                # Single-quoted path: immunte to backslashes & spaces
                # Semicolon separates statements in PowerShell
                ps_script = f"Set-Location '{project_path}'; {command}"
            else:
                ps_script = command  # just run from default location

            logger.info(f"Launching PowerShell: {ps_script}")

            # CREATE_NEW_CONSOLE opens a separate, visible PowerShell window
            subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoExit",       # keep window open after command finishes
                    "-NoProfile",    # faster startup — skip $PROFILE loading
                    "-Command", ps_script,
                ],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

            logger.info("PowerShell terminal launched successfully")
            return (
                f"Terminal opened  ->  '{command}'"
                + (f"  (in {project_path})" if project_path else "")
            )

        except FileNotFoundError:
            # PowerShell not found — fall back to cmd with shell=True
            logger.warning("powershell.exe not found — falling back to cmd")
            return self._run_in_cmd_fallback(project_path, command)

        except Exception as exc:
            msg = f"Failed to open terminal: {exc}"
            logger.error(msg)
            return msg

    def _run_in_cmd_fallback(self, project_path, command):
        """
        Fallback terminal launcher using cmd.exe with shell=True.
        shell=True lets Windows parse the full command string correctly,
        avoiding the quote-escaping problem of the list-args approach.

        Returns:
            str: Human-readable step result.
        """
        try:
            if project_path and os.path.isdir(project_path):
                # Use /d to allow cross-drive cd; wrap path only if it has spaces
                path_arg = f'"{project_path}"' if " " in project_path else project_path
                full_cmd = f'start cmd.exe /K "cd /d {path_arg} && {command}"'
            else:
                full_cmd = f'start cmd.exe /K "{command}"'

            logger.info(f"cmd fallback: {full_cmd}")
            subprocess.run(full_cmd, shell=True)
            return (
                f"Terminal opened (cmd)  ->  '{command}'"
                + (f"  (in {project_path})" if project_path else "")
            )
        except Exception as exc:
            msg = f"cmd fallback failed: {exc}"
            logger.error(msg)
            return msg


    def _open_url(self, url):
        """
        Open a URL in the system's default web browser.

        Args:
            url (str): URL to open.

        Returns:
            str: Human-readable step result.
        """
        try:
            # new=2 → open in a new tab if the browser is already running
            webbrowser.open(url, new=2)
            logger.info(f"Browser opened: {url}")
            return f"✅  Browser  →  {url}"
        except Exception as exc:
            msg = f"❌  Failed to open URL '{url}': {exc}"
            logger.error(msg)
            return msg
