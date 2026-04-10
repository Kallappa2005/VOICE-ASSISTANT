"""
Assistant Pipeline
Main orchestrator for the voice-first pipeline
Routes commands to appropriate handlers
"""

from src.agent.intent_enhancer import IntentEnhancer
from src.agent.task_planner import TaskPlanner
from src.agent.execution_manager import ExecutionManager
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class Assistant:
    """
    Main assistant orchestrator
    Routes commands through the pipeline:
    Voice → Text → Intent → Plan → Execute → UI Output
    """

    def __init__(self, tts=None, ui_callback=None):
        """
        Initialize assistant

        Args:
            tts: TextToSpeechHandler for voice feedback
            ui_callback: Function to update UI (progress, logs, etc.)
        """
        self.tts = tts
        self.ui_callback = ui_callback

        # Initialize pipeline components
        self.intent_enhancer = IntentEnhancer()
        self.task_planner = TaskPlanner()
        self.execution_manager = ExecutionManager(tts=tts)

        logger.info("Assistant initialized")

    # ──────────────────────────────────────────────────────────────────────
    # STEP 3: Detect Developer Task
    # ──────────────────────────────────────────────────────────────────────

    def is_developer_task(self, command: str) -> bool:
        """
        🎯 STEP 3: Detect if command is for developer automation

        Logic:
            Check if command contains developer keywords
            Examples:
                "build react project" → True
                "create node app" → True
                "setup express" → True
                "open wikipedia" → False
                "search google" → False

        Args:
            command (str): Raw text command from voice input

        Returns:
            bool: True if developer task, False otherwise
        """
        if not command:
            return False

        command_lower = command.lower().strip()

        # Developer task keywords
        developer_keywords = [
            "build",
            "create",
            "setup",
            "react",
            "node",
            "project",
            "app",
            "express",
            "fastify",
            "vite",
            "scaffold",
            "new",
        ]

        # Check if any keyword matches
        is_dev_task = any(kw in command_lower for kw in developer_keywords)

        logger.info(
            f"is_developer_task('{command}') → {is_dev_task}"
        )
        return is_dev_task

    # ──────────────────────────────────────────────────────────────────────
    # STEP 4: Handle Developer Task
    # ──────────────────────────────────────────────────────────────────────

    def handle_developer_task(self, command: str) -> dict:
        """
        🎯 STEP 4: Execute complete developer task flow

        Pipeline:
            ① IntentEnhancer.enhance()      - Extract structured intent
            ② TaskPlanner.plan()            - Generate ordered steps
            ③ UI + TTS feedback             - Show plan & speak confirmation
            ④ ExecutionManager.execute()    - Run steps sequentially
            ⑤ Report result                 - Show success/failure

        Args:
            command (str): Text command (e.g., "build react project my-port")

        Returns:
            dict: {
                "success": bool,
                "project_path": str | None,
                "completed_steps": int,
                "total_steps": int,
                "error": str | None
            }
        """
        try:
            logger.info(f"Developer task detected: '{command}'")

            # ─── ① Enhance Intent (Extract structured data) ───────────────────
            logger.info("Step 1: Enhancing intent...")
            self._ui_update(
                "step", 1, 5,
                "Analyzing command...",
            )

            enhanced = self.intent_enhancer.enhance(command)
            goal = enhanced.get("goal", "unknown")
            proj_name = enhanced.get("name") or f"app-{int(__import__('time').time())}"
            framework = enhanced.get("framework")

            logger.info(
                f"Enhanced intent: goal={goal}, "
                f"name={proj_name}, framework={framework}"
            )

            # ─── Speak intent ───────────────────────────────────────────────
            if self.tts:
                try:
                    self.tts.speak(
                        f"Creating {goal.replace('_', ' ')} project: {proj_name}"
                    )
                except Exception as exc:
                    logger.warning(f"TTS error: {exc}")

            # ─── ② Generate Plan (TaskPlanner) ──────────────────────────────
            logger.info("Step 2: Planning execution steps...")
            self._ui_update(
                "step", 2, 5,
                "Generating execution plan...",
            )

            steps = self.task_planner.plan(enhanced)
            if not steps:
                error_msg = (
                    f"Could not generate plan for: {goal}"
                )
                logger.error(error_msg)
                self._ui_update(
                    "error", None, None,
                    error_msg,
                )

                if self.tts:
                    try:
                        self.tts.speak(
                            "I could not create a plan for this task"
                        )
                    except:
                        pass

                return {
                    "success": False,
                    "project_path": None,
                    "completed_steps": 0,
                    "total_steps": 0,
                    "error": error_msg,
                }

            # ─── Display plan in UI ─────────────────────────────────────────
            self._ui_update(
                "plan", None, None,
                self.task_planner.describe_plan(steps),
            )
            logger.info(f"Plan generated: {len(steps)} steps")

            # ─── Set GUI Project Info ───────────────────────────────────────
            self._set_gui_project_info(proj_name, goal)

            # ─── ③ UI + Voice Feedback (NO confirmation dialog) ──────────────
            # Skip user confirmation for speed (as per requirements)
            logger.info("Step 3: Starting execution (no confirmation needed)...")
            self._ui_update(
                "status", None, None,
                f"Starting execution: {len(steps)} steps",
            )

            if self.tts:
                try:
                    self.tts.speak(
                        f"Starting execution. "
                        f"This will take a few minutes."
                    )
                except:
                    pass

            # ─── ④ Execute Steps (ExecutionManager) ─────────────────────────
            logger.info("Step 4: Executing plan...")
            result = self.execution_manager.execute(
                steps,
                project_dir=None,  # Uses default: ~/Hackathon/
                ui_callback=self._ui_update,
            )

            # ─── ⑤ Report Result ────────────────────────────────────────────
            if result["success"]:
                logger.info(
                    f"Execution successful: {result['project_path']}"
                )
                self._ui_update(
                    "success", None, None,
                    f"Project created: {result['project_path']}",
                )

                if self.tts:
                    try:
                        self.tts.speak(
                            "Your project is ready and running"
                        )
                    except:
                        pass
            else:
                logger.error(f"Execution failed: {result['error']}")
                self._ui_update(
                    "error", None, None,
                    result["error"],
                )

                if self.tts:
                    try:
                        self.tts.speak(
                            "Sorry, the execution failed. "
                            "Check the console for details."
                        )
                    except:
                        pass

            return result

        except Exception as exc:
            logger.error(
                f"Developer task error: {exc}",
                exc_info=True,
            )
            error_msg = f"Unexpected error: {exc}"
            self._ui_update(
                "error", None, None,
                error_msg,
            )

            if self.tts:
                try:
                    self.tts.speak("An unexpected error occurred")
                except:
                    pass

            return {
                "success": False,
                "project_path": None,
                "completed_steps": 0,
                "total_steps": 0,
                "error": error_msg,
            }

    # ──────────────────────────────────────────────────────────────────────
    # UI Callback Helper
    # ──────────────────────────────────────────────────────────────────────

    def _ui_update(
        self,
        update_type: str,
        step_num: int | None,
        total_steps: int | None,
        message: str,
    ) -> None:
        """
        Internal helper to update UI

        Args:
            update_type: "step", "plan", "status", "success", "error"
            step_num: Current step number
            total_steps: Total steps
            message: Message to display
        """
        if not self.ui_callback:
            return

        try:
            self.ui_callback(
                {
                    "type": update_type,
                    "step": step_num,
                    "total": total_steps,
                    "message": message,
                }
            )
        except Exception as exc:
            logger.warning(f"UI callback error: {exc}")

    def _set_gui_project_info(self, proj_name: str, goal: str) -> None:
        """
        Update GUI with project information

        Args:
            proj_name: Project name
            goal: Goal/framework string
        """
        if not self.ui_callback:
            return

        try:
            # Determine framework
            if "react" in goal.lower():
                framework = "React + Vite"
            elif "express" in goal.lower():
                framework = "Node.js + Express"
            elif "fastify" in goal.lower():
                framework = "Node.js + Fastify"
            else:
                framework = "Node.js"

            # Get project location
            from pathlib import Path
            location = str(Path.home() / "Desktop" / "Hackathon")

            # Send GUI update
            self.ui_callback(
                {
                    "type": "project_info",
                    "project_name": proj_name,
                    "framework": framework,
                    "location": location,
                }
            )
        except Exception as exc:
            logger.warning(f"GUI project info error: {exc}")
