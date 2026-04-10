"""
Simple UI Handler for Pipeline
Receives and displays updates from the execution pipeline
Can be extended later with GUI/Tkinter components
"""

from src.core.logger import setup_logger

logger = setup_logger(__name__)


class UIHandler:
    """Handle UI updates from the execution pipeline"""

    def __init__(self):
        """Initialize UI handler"""
        self.current_step = 0
        self.total_steps = 0
        logger.info("UIHandler initialized")

    def update(self, update_dict: dict) -> None:
        """
        Receive and process UI updates

        Args:
            update_dict (dict): Update with keys:
                - type: "step_start", "step_complete", "success", "error", "status", "plan"
                - step: current step number
                - total: total steps
                - message: display message
                - status: "success", "failed", etc.
        """
        update_type = update_dict.get("type")
        step = update_dict.get("step")
        total = update_dict.get("total")
        message = update_dict.get("message", "")
        status = update_dict.get("status", "")

        # Store current progress
        if step:
            self.current_step = step
        if total:
            self.total_steps = total

        # Log all updates
        logger.info(f"UI Update: {update_type} - {message}")

        # Display based on update type
        if update_type == "step_start":
            print(f"\n  [{step}/{total}] {message} ...")

        elif update_type == "step_complete":
            if status == "success":
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")

        elif update_type == "status":
            print(f"\n  [STATUS] {message}")

        elif update_type == "plan":
            print(f"\n  [PLAN]")
            print(f"  {'=' * 50}")
            for line in message.split("\n"):
                print(f"  {line}")
            print(f"  {'=' * 50}")

        elif update_type == "success":
            print(f"\n  ✓ SUCCESS")
            print(f"  {message}")

        elif update_type == "error":
            print(f"\n  ✗ ERROR")
            print(f"  {message}")

    def get_progress(self) -> dict:
        """Get current progress"""
        return {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percent": (
                (self.current_step / self.total_steps * 100)
                if self.total_steps > 0
                else 0
            ),
        }
