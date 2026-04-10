"""
Intent Enhancer
===============
Converts raw command text (already lightly parsed by CommandParser) into
a structured JSON-style intent dict that the TaskPlanner can consume.

Detection strategy (in priority order)
---------------------------------------
1. Rule-based keyword matching  — fast, zero API cost, handles 95 % of cases
2. Gemini fallback              — only when rules return 'unknown_developer_task'

Does NOT modify CommandParser — it sits AFTER the parser in the pipeline.

Returned intent dict shape
--------------------------
{
    "type":       "developer_task" | "simple_command",
    "goal":       "create_react_project" | "create_node_project" | ...,
    "name":       "<project name or None>",
    "framework":  "express" | "fastify" | None,
    "raw_text":   "<original command string>"
}
"""

import re
from src.core.logger import setup_logger

logger = setup_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Keyword maps
# ─────────────────────────────────────────────────────────────────────────────

_REACT_KEYWORDS = [
    'react', 'vite react', 'create react', 'build react',
    'new react', 'react project', 'react app',
]

_NODE_KEYWORDS = [
    'node', 'node app', 'node project', 'node server',
    'create node', 'build node', 'new node',
    'express', 'express app', 'express server', 'express project',
    'fastify', 'fastify app',
]

_FRAMEWORK_MAP = {
    'express':  'express',
    'fastify':  'fastify',
    'koa':      'koa',
    'hapi':     'hapi',
}


# ─────────────────────────────────────────────────────────────────────────────
# Main class
# ─────────────────────────────────────────────────────────────────────────────

class IntentEnhancer:
    """
    Enhances a raw voice command into a structured intent dict.

    Usage
    -----
        enhancer = IntentEnhancer()
        intent   = enhancer.enhance("build react project called my-dashboard")
        # → {"type": "developer_task", "goal": "create_react_project",
        #     "name": "my-dashboard", "framework": None, "raw_text": "..."}
    """

    def __init__(self, gemini_client=None):
        """
        Args:
            gemini_client: Optional GeminiClient instance for fallback
                           classification. If None, Gemini fallback is skipped
                           and ambiguous commands return type='simple_command'.
        """
        self.gemini_client = gemini_client
        logger.info("IntentEnhancer initialised "
                    f"(Gemini fallback: {'enabled' if gemini_client else 'disabled'})")

    # ── Public API ────────────────────────────────────────────────────────────

    def enhance(self, raw_text: str, parsed_intent: dict | None = None) -> dict:
        """
        Main entry point.

        Args:
            raw_text (str):       The original voice/text command.
            parsed_intent (dict): Optional dict from CommandParser (may be None).

        Returns:
            dict: Structured intent.
        """
        if not raw_text:
            logger.warning("IntentEnhancer received empty text")
            return self._simple(raw_text)

        text = raw_text.lower().strip()
        logger.info(f"Enhancing intent for: '{text}'")

        # ── 1. Rule-based React detection ─────────────────────────────────────
        if self._matches_any(text, _REACT_KEYWORDS):
            name = self._extract_project_name(text)
            result = {
                "type":      "developer_task",
                "goal":      "create_react_project",
                "name":      name,
                "framework": None,
                "raw_text":  raw_text,
            }
            logger.info(f"Rule match → React project (name={name})")
            return result

        # ── 2. Rule-based Node detection ──────────────────────────────────────
        if self._matches_any(text, _NODE_KEYWORDS):
            name      = self._extract_project_name(text)
            framework = self._extract_framework(text)
            result = {
                "type":      "developer_task",
                "goal":      "create_node_project",
                "name":      name,
                "framework": framework,
                "raw_text":  raw_text,
            }
            logger.info(f"Rule match → Node project (name={name}, framework={framework})")
            return result

        # ── 3. Gemini fallback ────────────────────────────────────────────────
        if self.gemini_client:
            gemini_result = self._gemini_classify(text)
            if gemini_result:
                logger.info(f"Gemini classified as developer task: {gemini_result}")
                return gemini_result

        # ── 4. Not a developer task ───────────────────────────────────────────
        logger.info("No developer task detected — returning simple_command")
        return self._simple(raw_text)

    def is_developer_task(self, raw_text: str) -> bool:
        """
        Quick check: does this text look like a developer task?
        Used by main_ai.py to decide whether to route to the agent pipeline.

        Args:
            raw_text (str): Command text.

        Returns:
            bool: True if it looks like a developer task.
        """
        text = raw_text.lower().strip()
        return (
            self._matches_any(text, _REACT_KEYWORDS) or
            self._matches_any(text, _NODE_KEYWORDS)
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _matches_any(text: str, keywords: list[str]) -> bool:
        """Return True if text contains any keyword from the list."""
        return any(kw in text for kw in keywords)

    @staticmethod
    def _extract_project_name(text: str) -> str | None:
        """
        Try to pull a project name from the command.

        Patterns recognised
        -------------------
          "... called my-app"
          "... named my-app"
          "... project my-app"
          "... app my-app"
          "build react my-dashboard"
        """
        # Pattern: 'called X' or 'named X'
        m = re.search(r'\b(?:called|named)\s+([\w-]+)', text)
        if m:
            return m.group(1)

        # Pattern: 'project X' or 'app X' where X looks like an identifier
        m = re.search(r'\b(?:project|app)\s+([\w-]+)', text)
        if m:
            candidate = m.group(1)
            # Reject generic noise words
            noise = {'with', 'using', 'and', 'the', 'a', 'an', 'in', 'to'}
            if candidate not in noise:
                return candidate

        return None  # caller will auto-generate a name

    @staticmethod
    def _extract_framework(text: str) -> str | None:
        """Detect which Node framework was requested."""
        for keyword, framework in _FRAMEWORK_MAP.items():
            if keyword in text:
                return framework
        return 'express'  # sensible default for Node projects

    def _gemini_classify(self, text: str) -> dict | None:
        """
        Ask Gemini to classify the command.
        Returns a structured intent dict, or None on failure.
        """
        prompt = (
            "Classify this voice command as a developer task or not.\n"
            "Reply with ONLY a JSON object — no markdown, no extra text.\n\n"
            f"Command: \"{text}\"\n\n"
            "If it is a developer task, return:\n"
            '{"type":"developer_task","goal":"create_react_project OR create_node_project",'
            '"name":"<project name or null>","framework":"<framework or null>"}\n\n'
            "If NOT a developer task, return:\n"
            '{"type":"simple_command"}'
        )
        try:
            import json
            response = self.gemini_client.generate(prompt)
            # Strip markdown fences if present
            clean = re.sub(r'```[a-z]*\n?', '', response).strip()
            data  = json.loads(clean)
            if data.get("type") == "developer_task":
                data["raw_text"] = text
                return data
            return None
        except Exception as exc:
            logger.warning(f"Gemini fallback failed: {exc}")
            return None

    @staticmethod
    def _simple(raw_text: str) -> dict:
        """Return a simple_command intent (non-developer task)."""
        return {
            "type":      "simple_command",
            "goal":      None,
            "name":      None,
            "framework": None,
            "raw_text":  raw_text,
        }
