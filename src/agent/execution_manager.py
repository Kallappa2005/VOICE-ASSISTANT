"""
Execution Manager
=================
Responsible for:
  1. Printing the plan to the console before anything runs
  2. Asking the user for explicit confirmation
  3. Executing each step safely (subprocess / filesystem)

Public API
----------
    mgr = ExecutionManager(tts=tts_handler)   # tts is optional
    mgr.show_plan(steps)                       # print numbered plan
    confirmed = mgr.confirm()                  # True / False
    result    = mgr.execute(steps, project_dir=r"C:\\Dev")

Helper functions (module-level, importable separately)
------------------------------------------------------
    check_node_installed()  → bool
    run_command(cmd, cwd)   → (success: bool, output: str)
    create_file(path, text) → bool
    open_browser_tab(url)   → bool
"""

import os
import re
import subprocess
import webbrowser
from pathlib import Path

from src.core.logger import setup_logger
from src.agent.code_templates import get_template
from src.agent.task_planner import TaskPlanner

logger = setup_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Module-level helper functions
# ─────────────────────────────────────────────────────────────────────────────

def check_node_installed() -> bool:
    """
    Verify that Node.js (and npm) are available on PATH.

    Returns:
        bool: True if `node --version` exits successfully.
    """
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            logger.info(f"Node.js found: {version}")
            print(f"   [OK]  Node.js detected -> {version}")
            return True
        logger.warning("node --version returned non-zero exit code")
        return False
    except FileNotFoundError:
        logger.error("Node.js not found on PATH")
        return False
    except Exception as exc:
        logger.error(f"check_node_installed error: {exc}")
        return False


def run_command(cmd: list[str] | str, cwd: str | None = None,
                blocking: bool = True) -> tuple[bool, str]:
    """
    Run a shell command, optionally in a given working directory.

    Args:
        cmd (list | str): Command and arguments.
        cwd (str | None): Working directory. Defaults to current dir.
        blocking (bool):  If True, wait for completion and return output.
                          If False, spawn in a new PowerShell window and
                          return immediately (used for dev servers).

    Returns:
        tuple[bool, str]: (success, stdout/stderr or status message)
    """
    try:
        if not blocking:
            # Open a visible, persistent terminal for long-running processes
            if isinstance(cmd, list):
                cmd_str = " ".join(str(c) for c in cmd)
            else:
                cmd_str = cmd

            ps_script = (
                f"Set-Location '{cwd}'; {cmd_str}"
                if cwd and os.path.isdir(cwd)
                else cmd_str
            )
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-NoProfile", "-Command", ps_script],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            logger.info(f"Non-blocking command launched: {cmd_str}")
            return True, "Process launched in new terminal"

        # Blocking execution
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300,          # 5-minute safety timeout
            shell=isinstance(cmd, str),
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0:
            logger.info(f"Command succeeded: {cmd}")
            return True, output.strip()
        else:
            logger.error(f"Command failed (rc={result.returncode}): {cmd}\n{output}")
            return False, output.strip()

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {cmd}")
        return False, "Command timed out after 5 minutes"
    except FileNotFoundError as exc:
        logger.error(f"Command not found: {exc}")
        return False, f"Command not found: {exc}"
    except Exception as exc:
        logger.error(f"run_command error: {exc}")
        return False, str(exc)


def create_file(path: str, content: str) -> bool:
    """
    Write content to a file, creating parent directories as needed.

    Args:
        path (str):    Absolute or relative file path.
        content (str): Text content to write.

    Returns:
        bool: True on success.
    """
    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        logger.info(f"File created: {path}")
        return True
    except Exception as exc:
        logger.error(f"create_file error ({path}): {exc}")
        return False


def open_browser_tab(url: str) -> bool:
    """
    Open a URL in the system's default browser (new tab).

    Args:
        url (str): URL to open.

    Returns:
        bool: True on success.
    """
    try:
        webbrowser.open(url, new=2)
        logger.info(f"Browser tab opened: {url}")
        return True
    except Exception as exc:
        logger.error(f"open_browser_tab error ({url}): {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# ExecutionManager class
# ─────────────────────────────────────────────────────────────────────────────

class ExecutionManager:
    """
    Shows, confirms, and executes a task plan.

    Args:
        tts: Optional TextToSpeechHandler instance for voice feedback.
        planner: Optional TaskPlanner for describe_plan(). One is created
                 internally if not supplied.
    """

    def __init__(self, tts=None, planner: TaskPlanner | None = None):
        self.tts     = tts
        self.planner = planner or TaskPlanner()
        logger.info("ExecutionManager initialised")

    # ── Plan display ──────────────────────────────────────────────────────────

    def show_plan(self, steps: list[dict]) -> None:
        """
        Print the execution plan to the console in a clear numbered format.

        Args:
            steps (list[dict]): Step list from TaskPlanner.plan().
        """
        print("\n" + "=" * 65)
        print("[PLAN]  EXECUTION PLAN")
        print("=" * 65)
        print("\nI will perform these steps:\n")
        print(self.planner.describe_plan(steps))
        print("\n" + "=" * 65)
        logger.info(f"Plan displayed ({len(steps)} steps)")

    # ── Confirmation ──────────────────────────────────────────────────────────

    def confirm(self, prompt: str | None = None) -> bool:
        """
        Ask the user for confirmation via console input.

        Args:
            prompt (str | None): Override the default prompt.

        Returns:
            bool: True if user typed 'yes' / 'y', False otherwise.
        """
        default_prompt = "\n?  Do you want to continue? (yes / no): "
        try:
            answer = input(prompt or default_prompt).strip().lower()
            confirmed = answer in ("yes", "y")
            logger.info(f"User confirmation: '{answer}' -> {confirmed}")
            if not confirmed:
                print("\n[CANCELLED]  Execution cancelled by user.\n")
            return confirmed
        except (EOFError, KeyboardInterrupt):
            logger.warning("Confirmation interrupted -- treating as 'no'")
            print("\n[CANCELLED]  Execution cancelled.\n")
            return False

    # ── Execution ─────────────────────────────────────────────────────────────

    def execute(self, steps: list[dict],
                project_dir: str | None = None) -> dict:
        """
        Execute each step in sequence.  Stops safely on first failure.

        Args:
            steps (list[dict]):    Step list from TaskPlanner.plan().
            project_dir (str):     Base directory where projects are created.
                                   Defaults to the user's home directory.

        Returns:
            dict: {
                "success": bool,
                "completed_steps": int,
                "total_steps": int,
                "project_path": str | None,
                "error": str | None
            }
        """
        base_dir     = project_dir or str(Path.home())
        project_path = None          # filled in once folder / vite scaffold runs
        completed    = 0

        print("\n" + "=" * 65)
        print("[RUN]  EXECUTING PLAN")
        print("=" * 65 + "\n")
        logger.info(f"Execution started ({len(steps)} steps, base_dir={base_dir})")

        for i, step in enumerate(steps, 1):
            step_name = step.get("step", "unknown")
            print(f"  [{i}/{len(steps)}] {self.planner._describe_step(step)} …")

            try:
                ok, project_path = self._run_step(
                    step, base_dir, project_path
                )
            except Exception as exc:
                logger.error(f"Unhandled error in step '{step_name}': {exc}",
                             exc_info=True)
                ok = False
                print(f"         [ERR]  Unexpected error: {exc}")

            if ok:
                completed += 1
                print(f"         [OK]  Done\n")
            else:
                print(f"\n[FAIL]  Step failed: {step_name}. "
                      f"Stopping execution.\n")
                logger.error(f"Execution halted at step {i}: {step_name}")
                return {
                    "success":         False,
                    "completed_steps": completed,
                    "total_steps":     len(steps),
                    "project_path":    project_path,
                    "error":           f"Failed at step: {step_name}",
                }

        # ── All steps succeeded ───────────────────────────────────────────────
        print("=" * 65)
        print("[DONE]  All steps completed successfully!")
        print(f"[DIR]   Project location: {project_path or base_dir}")
        print("=" * 65 + "\n")
        logger.info(f"Execution finished: {completed}/{len(steps)} steps OK")

        if self.tts:
            try:
                self.tts.speak("Your project is ready and running.")
            except Exception:
                pass

        return {
            "success":         True,
            "completed_steps": completed,
            "total_steps":     len(steps),
            "project_path":    project_path,
            "error":           None,
        }

    # ── Step router ───────────────────────────────────────────────────────────

    def _run_step(self, step: dict, base_dir: str,
                  project_path: str | None) -> tuple[bool, str | None]:
        """
        Dispatch a single step to the correct handler.

        Returns:
            tuple[bool, str | None]: (success, updated_project_path)
        """
        s = step.get("step")

        # ── check_node ────────────────────────────────────────────────────────
        if s == "check_node":
            ok = check_node_installed()
            if not ok:
                print(
                    "         [WARN]  Node.js is not installed or not on PATH.\n"
                    "         Please install Node.js >= 18 from https://nodejs.org\n"
                )
            return ok, project_path

        # ── create_react_app (Vite) ───────────────────────────────────────────
        if s == "create_react_app":
            name = step.get("name", "react-app")
            ok, out = run_command(
                ["npm", "create", "vite@latest", name, "--", "--template", "react"],
                cwd=base_dir,
            )
            if ok:
                new_path = str(Path(base_dir) / name)
                print(f"         [DIR]  Created at: {new_path}")
                return True, new_path
            print(f"         Output:\n{out}")
            return False, project_path

        # ── create_folder ─────────────────────────────────────────────────────
        if s == "create_folder":
            name     = step.get("name", "node-app")
            new_path = str(Path(base_dir) / name)
            try:
                Path(new_path).mkdir(parents=True, exist_ok=True)
                print(f"         [DIR]  Created at: {new_path}")
                logger.info(f"Folder created: {new_path}")
                return True, new_path
            except Exception as exc:
                print(f"         ❌  {exc}")
                return False, project_path

        # ── npm_init ──────────────────────────────────────────────────────────
        if s == "npm_init":
            cwd = project_path or base_dir
            ok, out = run_command(["npm", "init", "-y"], cwd=cwd)
            if not ok:
                print(f"         Output:\n{out}")
            return ok, project_path

        # ── install_dependencies ──────────────────────────────────────────────
        if s == "install_dependencies":
            cwd      = project_path or base_dir
            packages = step.get("packages")
            if packages:
                cmd = ["npm", "install"] + packages
            else:
                cmd = ["npm", "install"]
            ok, out = run_command(cmd, cwd=cwd)
            if not ok:
                print(f"         Output:\n{out}")
            return ok, project_path

        # ── create_file ───────────────────────────────────────────────────────
        if s == "create_file":
            filename  = step.get("name", "server.js")
            file_path = str(Path(project_path or base_dir) / filename)
            # Write a blank placeholder — write_code fills it next
            ok = create_file(file_path, "")
            return ok, project_path

        # ── write_code ────────────────────────────────────────────────────────
        if s == "write_code":
            template_name = step.get("template", "express_server")
            filename      = "server.js"   # default target for node projects
            file_path     = str(Path(project_path or base_dir) / filename)
            try:
                code = get_template(template_name)
                ok   = create_file(file_path, code)
                return ok, project_path
            except KeyError as exc:
                print(f"         ❌  Template error: {exc}")
                return False, project_path

        # ── start_dev_server ──────────────────────────────────────────────────
        if s == "start_dev_server":
            cwd = project_path or base_dir
            ok, msg = run_command(
                ["npm", "run", "dev"],
                cwd=cwd,
                blocking=False,    # opens new terminal window
            )
            print(f"         [i]  {msg}")
            return ok, project_path

        # ── run_server ────────────────────────────────────────────────────────
        if s == "run_server":
            cwd = project_path or base_dir
            ok, msg = run_command(
                ["node", "server.js"],
                cwd=cwd,
                blocking=False,    # opens new terminal window
            )
            print(f"         [i]  {msg}")
            return ok, project_path

        # ── open_browser ──────────────────────────────────────────────────────
        if s == "open_browser":
            url = step.get("url", "http://localhost:3000")
            ok  = open_browser_tab(url)
            return ok, project_path

        # ── Unknown step ──────────────────────────────────────────────────────
        logger.warning(f"Unknown step type: '{s}' -- skipping")
        print(f"         [SKIP]  Unknown step '{s}' -- skipped")
        return True, project_path   # skip unknown steps, don't abort
