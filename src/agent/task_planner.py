"""
Task Planner
============
Converts a structured intent dict (from IntentEnhancer) into an ordered
list of execution steps that ExecutionManager can run.

Step dict shape
---------------
Each step is a plain dict with at least a "step" key:

    {"step": "check_node"}
    {"step": "create_react_app",      "name": "react-app-1713000000"}
    {"step": "install_dependencies"}
    {"step": "start_dev_server"}
    {"step": "open_browser",          "url": "http://localhost:5173"}

    {"step": "create_folder",         "name": "node-app-1713000000"}
    {"step": "npm_init"}
    {"step": "install_dependencies",  "packages": ["express"]}
    {"step": "create_file",           "name": "server.js"}
    {"step": "write_code",            "template": "express_server"}
    {"step": "run_server"}
"""

import time
from src.core.logger import setup_logger

logger = setup_logger(__name__)

# ── Framework → npm packages mapping ─────────────────────────────────────────
_FRAMEWORK_PACKAGES: dict[str, list[str]] = {
    'express':  ['express'],
    'fastify':  ['fastify'],
    'koa':      ['koa', 'koa-router'],
    'hapi':     ['@hapi/hapi'],
}

# Default packages for a Node project when no framework is specified
_DEFAULT_NODE_PACKAGES = ['express']

# Dev server port per tool
_REACT_DEV_PORT = 5173   # Vite default
_NODE_DEV_PORT  = 3000   # Express / generic default


class TaskPlanner:
    """
    Generates ordered step plans from structured intents.

    Usage
    -----
        planner = TaskPlanner()
        steps   = planner.plan({"type": "developer_task",
                                "goal": "create_react_project",
                                "name": None, ...})
    """

    def __init__(self):
        logger.info("TaskPlanner initialised")

    # ── Public API ────────────────────────────────────────────────────────────

    def plan(self, intent: dict) -> list[dict]:
        """
        Generate an execution plan from an intent dict.

        Args:
            intent (dict): Structured intent from IntentEnhancer.

        Returns:
            list[dict]: Ordered list of step dicts.
                        Returns an empty list for non-developer tasks.
        """
        try:
            goal = intent.get("goal")

            if goal == "create_react_project":
                return self._plan_react(intent)

            if goal == "create_node_project":
                return self._plan_node(intent)

            logger.warning(f"No plan available for goal: '{goal}'")
            return []

        except Exception as exc:
            logger.error(f"TaskPlanner.plan() error: {exc}", exc_info=True)
            return []

    def describe_plan(self, steps: list[dict]) -> str:
        """
        Return a human-readable numbered description of the plan.
        Used for printing to console and the UI log.

        Args:
            steps (list[dict]): Output from plan().

        Returns:
            str: Multi-line text.
        """
        if not steps:
            return "  (no steps)"

        lines = []
        for i, step in enumerate(steps, 1):
            lines.append(f"  {i}. {self._describe_step(step)}")
        return "\n".join(lines)

    # ── React plan ────────────────────────────────────────────────────────────

    def _plan_react(self, intent: dict) -> list[dict]:
        name = intent.get("name") or self._auto_name("react-app")
        url  = f"http://localhost:{_REACT_DEV_PORT}"

        steps = [
            {"step": "check_node"},
            {"step": "create_react_app",     "name": name},
            {"step": "install_dependencies"},
            {"step": "start_dev_server"},
            {"step": "open_browser",         "url": url},
        ]

        logger.info(f"React plan generated: name={name}, {len(steps)} steps")
        return steps

    # ── Node plan ─────────────────────────────────────────────────────────────

    def _plan_node(self, intent: dict) -> list[dict]:
        name      = intent.get("name")     or self._auto_name("node-app")
        framework = intent.get("framework") or "express"
        packages  = _FRAMEWORK_PACKAGES.get(framework, _DEFAULT_NODE_PACKAGES)

        steps = [
            {"step": "check_node"},
            {"step": "create_folder",        "name": name},
            {"step": "npm_init"},
            {"step": "install_dependencies", "packages": packages},
            {"step": "create_file",          "name": "server.js"},
            {"step": "write_code",           "template": "express_server"},
            {"step": "run_server"},
        ]

        logger.info(
            f"Node plan generated: name={name}, framework={framework}, "
            f"packages={packages}, {len(steps)} steps"
        )
        return steps

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _auto_name(prefix: str) -> str:
        """
        Generate a unique project name using a Unix timestamp suffix.

        Example: 'react-app-1713001234'
        """
        suffix = str(int(time.time()))
        return f"{prefix}-{suffix}"

    @staticmethod
    def _describe_step(step: dict) -> str:
        """Convert a step dict to a short human-readable string."""
        s = step.get("step", "?")

        descriptions = {
            "check_node":           "Check Node.js is installed",
            "create_react_app":     f"Create React app (Vite) -> '{step.get('name', '')}'",
            "install_dependencies": (
                f"Install packages: {', '.join(step['packages'])}"
                if "packages" in step else "Run npm install"
            ),
            "start_dev_server":     "Start dev server (npm run dev)",
            "open_browser":         f"Open browser -> {step.get('url', '')}",
            "create_folder":        f"Create project folder -> '{step.get('name', '')}'",
            "npm_init":             "Initialise package.json (npm init -y)",
            "create_file":          f"Create file -> {step.get('name', '')}",
            "write_code":           f"Write template code ({step.get('template', '')})",
            "run_server":           "Start Node server (node server.js)",
        }

        return descriptions.get(s, f"[{s}]")
