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
import platform
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


def is_port_in_use(port: int = 5173) -> bool:
    """
    Check if a port is already in use (Phase 2: Port conflict detection).
    
    Args:
        port (int): Port number to check (default: 5173 for Vite)
    
    Returns:
        bool: True if port is in use, False otherwise
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            in_use = result == 0
            if in_use:
                logger.warning(f"Port {port} is already in use")
            return in_use
    except Exception as e:
        logger.warning(f"Could not check port {port}: {e}")
        return False


def run_command(cmd: list[str] | str, cwd: str | None = None,
                blocking: bool = True, retries: int = 1, 
                stream_output: bool = False) -> tuple[bool, str]:
    """
    Run a shell command with Windows support, retries, and optional streaming.
    
    ⚠️ WINDOWS FIX: Uses shell=True on Windows to find npm/node in PATH
    
    Args:
        cmd (list | str):      Command and arguments.
        cwd (str | None):      Working directory. Defaults to current dir.
        blocking (bool):       If True, wait for completion and return output.
                               If False, spawn in a new PowerShell window.
        retries (int):         Number of retries for transient failures (default: 1)
        stream_output (bool):  Whether to stream output during execution (for npm install, etc.)

    Returns:
        tuple[bool, str]: (success, stdout/stderr or status message)
    """
    import time
    
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

        # Blocking execution with retry logic
        is_windows = platform.system() == "Windows"
        use_shell = isinstance(cmd, str) or is_windows
        
        if isinstance(cmd, list) and is_windows:
            cmd = " ".join(str(c) for c in cmd)
        
        last_error = None
        for attempt in range(retries):
            try:
                if stream_output:
                    # Stream output in real-time
                    process = subprocess.Popen(
                        cmd,
                        cwd=cwd,
                        shell=use_shell,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    output_lines = []
                    for line in process.stdout:
                        print(f"         {line.rstrip()}")  # Live output
                        output_lines.append(line)
                    process.wait()
                    output = "".join(output_lines)
                    
                    if process.returncode == 0:
                        logger.info(f"Command succeeded (attempt {attempt+1}): {cmd}")
                        return True, output.strip()
                    else:
                        last_error = output
                else:
                    # Standard execution
                    result = subprocess.run(
                        cmd,
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        shell=use_shell,
                    )
                    output = (result.stdout or "") + (result.stderr or "")
                    if result.returncode == 0:
                        logger.info(f"Command succeeded (attempt {attempt+1}): {cmd}")
                        return True, output.strip()
                    else:
                        last_error = output
                
                # If we need to retry
                if attempt < retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                    logger.warning(f"Command failed (attempt {attempt+1}), retrying in {wait_time}s...")
                    print(f"         [RETRY] Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out (attempt {attempt+1}): {cmd}")
                last_error = "Command timed out after 5 minutes"
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        
        # All retries exhausted
        logger.error(f"Command failed after {retries} attempt(s): {cmd}\n{last_error}")
        return False, last_error or "Command failed"

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
    
    Phase 2: If port 5173 fails (in use), try fallback ports 5174, 5175, etc.

    Args:
        url (str): URL to open (e.g., http://localhost:5173)

    Returns:
        bool: True on success.
    """
    try:
        webbrowser.open(url, new=2)
        logger.info(f"Browser tab opened: {url}")
        return True
    except Exception as exc:
        # Phase 2: Try fallback ports
        if "localhost:5173" in url or "localhost:3000" in url:
            logger.warning(f"Failed to open {url}, trying fallback ports...")
            for port in [5174, 5175, 5176, 3001, 3002]:
                fallback_url = url.split(":")[:-1]  # Remove port
                fallback_url = ":".join(fallback_url) + f":{port}"
                try:
                    webbrowser.open(fallback_url, new=2)
                    logger.info(f"Browser tab opened (fallback): {fallback_url}")
                    print(f"         [OPEN]  Opened browser at {fallback_url}")
                    return True
                except:
                    continue
        
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
        ui_callback: Optional function to receive live UI updates.
    """

    def __init__(self, tts=None, planner: TaskPlanner | None = None, ui_callback=None):
        self.tts     = tts
        self.planner = planner or TaskPlanner()
        self.ui_callback = ui_callback
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
                project_dir: str | None = None,
                ui_callback=None) -> dict:
        """
        Execute each step in sequence.  Stops safely on first failure.

        Args:
            steps (list[dict]):    Step list from TaskPlanner.plan().
            project_dir (str):     Base directory where projects are created.
                                   Defaults to the user's home directory.
            ui_callback (callable): Optional function to receive live updates.

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
        
        # Allow override of ui_callback
        cb = ui_callback or self.ui_callback
        
        # Ensure Hackathon folder exists (default location for projects)
        if not project_dir:
            hackathon_root = Path.home() / "Desktop" / "Hackathon"
            hackathon_root.mkdir(parents=True, exist_ok=True)
            base_dir = str(hackathon_root)
            logger.info(f"Using Hackathon root: {base_dir}")

        print("\n" + "=" * 65)
        print("[RUN]  EXECUTING PLAN")
        print("=" * 65 + "\n")
        logger.info(f"Execution started ({len(steps)} steps, base_dir={base_dir})")

        for i, step in enumerate(steps, 1):
            step_name = step.get("step", "unknown")
            description = self.planner._describe_step(step)
            
            # UI callback: step started
            if cb:
                try:
                    cb({
                        "type": "step_start",
                        "step": i,
                        "total": len(steps),
                        "message": description,
                    })
                except:
                    pass
            
            print(f"  [{i}/{len(steps)}] {description} …")

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
                
                # UI callback: step complete
                if cb:
                    try:
                        cb({
                            "type": "step_complete",
                            "step": i,
                            "total": len(steps),
                            "status": "success",
                            "message": f"✓ {description}",
                        })
                    except:
                        pass
            else:
                print(f"\n[FAIL]  Step failed: {step_name}. "
                      f"Stopping execution.\n")
                logger.error(f"Execution halted at step {i}: {step_name}")
                
                # UI callback: step failed
                if cb:
                    try:
                        cb({
                            "type": "step_complete",
                            "step": i,
                            "total": len(steps),
                            "status": "failed",
                            "message": f"✗ {description}",
                        })
                    except:
                        pass
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
                retries=2,           # Retry once if network fails
                stream_output=True,  # Show live npm output
            )
            if ok:
                new_path = str(Path(base_dir) / name)
                print(f"         [DIR]  Created at: {new_path}")
                return True, new_path
            print(f"         Error:\n{out}")
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
            ok, out = run_command(
                cmd,
                cwd=cwd,
                retries=2,           # Network can fail, retry
                stream_output=True,  # npm install output is useful to watch
            )
            if not ok:
                print(f"         Error:\n{out}")
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
            
            # Phase 2: Check for port conflicts (Vite default: 5173)
            if is_port_in_use(5173):
                print(f"         [WARN]  Port 5173 is already in use")
                print(f"         [INFO]  Vite will use next available port (5174, 5175, ...)")
            
            ok, msg = run_command(
                ["npm", "run", "dev"],
                cwd=cwd,
                blocking=False,    # opens new terminal window
            )
            if ok:
                print(f"         [OK]  Dev server started")
                print(f"         [URL]  Visit http://localhost:5173 (or next available port)")
            else:
                print(f"         [ERROR]  {msg}")
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
            # Phase 2: Use Vite default port 5173 instead of 3000
            url = step.get("url", "http://localhost:5173")
            print(f"         [OPEN]  Opening browser to {url}...")
            ok  = open_browser_tab(url)
            if ok:
                print(f"         [OK]  Browser opened")
            return ok, project_path

        # ── Unknown step ──────────────────────────────────────────────────────
        logger.warning(f"Unknown step type: '{s}' -- skipping")
        print(f"         [SKIP]  Unknown step '{s}' -- skipped")
        return True, project_path   # skip unknown steps, don't abort
