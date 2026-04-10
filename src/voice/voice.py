"""
Voice Input Handler
Wrapper around SpeechRecognitionHandler for pipeline
Converts microphone audio → text string
"""

from src.speech.speech_recognition_handler import SpeechRecognitionHandler
from src.core.logger import setup_logger

logger = setup_logger(__name__)


class VoiceInput:
    """Handle voice input and conversion to text"""

    def __init__(self):
        """Initialize voice input handler"""
        self.stt = SpeechRecognitionHandler()
        logger.info("VoiceInput initialized")

    def listen(self) -> str | None:
        """
        Listen to microphone and convert speech to text

        Flow:
            1. Activate microphone
            2. Record audio until silence
            3. Convert to text using Google Speech Recognition
            4. Return lowercase clean string

        Returns:
            str | None: Recognized text, or None if failed

        Examples:
            "build react project my-portfolio"
            "open wikipedia machine learning"
            "analyze this page"
        """
        try:
            logger.info("Listening for voice input...")
            command = self.stt.listen()

            if not command:
                logger.warning("No voice input detected")
                return None

            # Clean and normalize
            command_clean = command.strip().lower()
            logger.info(f"Recognized: '{command_clean}'")
            return command_clean

        except Exception as exc:
            logger.error(f"Voice recognition error: {exc}")
            return None

    def calibrate(self, duration: float = 1.0) -> None:
        """
        Calibrate to room noise

        Args:
            duration (float): Seconds to sample ambient noise
        """
        try:
            logger.info(f"Calibrating microphone ({duration}s)...")
            self.stt.calibrate(duration=duration)
            logger.info("Calibration complete")
        except Exception as exc:
            logger.error(f"Calibration failed: {exc}")
