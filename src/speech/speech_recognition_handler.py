"""
Speech Recognition Handler
Listens to user voice commands and converts to text
Optimized for noisy environments (crowded rooms, background chatter)
"""

import speech_recognition as sr
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class SpeechRecognitionHandler:
    """Handles speech recognition for voice input — optimized for noisy rooms"""
    
    def __init__(self, language='en-IN', timeout=7, phrase_time_limit=12):
        """
        Initialize speech recognizer for noisy room conditions
        
        Args:
            language (str): Recognition language (en-IN for Indian English)
            timeout (int): Seconds to wait for speech to start (increased for noisy rooms)
            phrase_time_limit (int): Maximum seconds for a phrase
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.max_retries = 3  # Retry up to 3 times on failure in noisy conditions
        
        # ── Noisy Room Tuning ──────────────────────────────────────────────────
        # Higher threshold = ignores more background noise before treating
        # audio as speech. 4000 is default; 6000-8000 suits a crowded room.
        self.recognizer.energy_threshold = 6000
        
        # Let the library auto-raise the threshold when background noise spikes
        self.recognizer.dynamic_energy_threshold = True
        
        # How aggressively to adapt to changing noise levels (lower = faster adapt)
        self.recognizer.dynamic_energy_adjustment_damping = 0.10
        
        # Speech must be THIS much louder than background to count as speech
        self.recognizer.dynamic_energy_ratio = 1.8
        
        # Seconds of silence after speech before the phrase is considered done
        # Slightly longer so background chatter doesn't split your command
        self.recognizer.pause_threshold = 1.0
        
        # Minimum seconds of non-speech audio to keep around a phrase
        self.recognizer.non_speaking_duration = 0.6
        
        logger.info(
            f"Speech Recognition Handler initialized "
            f"[Noisy-Room Mode | energy_threshold={self.recognizer.energy_threshold} | "
            f"pause_threshold={self.recognizer.pause_threshold}]"
        )
    
    def calibrate(self, duration=2.0):
        """
        Calibrate the recognizer to the current room noise level.
        Call this once at startup or whenever the noise level changes.
        
        Args:
            duration (float): Seconds to sample ambient noise (longer = more accurate)
        """
        try:
            with sr.Microphone() as source:
                print(f"\n🔧 Calibrating to room noise... (hold {duration:.0f}s)")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                print(f"✅ Calibrated — energy threshold set to "
                      f"{int(self.recognizer.energy_threshold)}")
                logger.info(
                    f"Calibrated to ambient noise: "
                    f"energy_threshold={self.recognizer.energy_threshold:.0f}"
                )
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            print(f"⚠️ Calibration failed, using default threshold: {e}")

    def listen(self):
        """
        Listen to microphone and convert speech to text.
        Retries automatically on noise-related failures (up to max_retries).
        
        Returns:
            str: Recognized text (lowercase) or None if all attempts failed
        """
        for attempt in range(1, self.max_retries + 1):
            result = self._listen_once(attempt)
            if result is not None:
                return result
            # On noise-related failure, try again without spamming the user
            if attempt < self.max_retries:
                print(f"   ↩️  Retrying... (attempt {attempt + 1}/{self.max_retries})")
        
        print("❌ Could not understand after multiple attempts. "
              "Try speaking louder or closer to the mic.")
        return None

    def _listen_once(self, attempt=1):
        """
        Single listen attempt — used internally by listen().
        
        Args:
            attempt (int): Current attempt number (for logging)
            
        Returns:
            str: Recognized text or None
        """
        try:
            with sr.Microphone() as source:
                if attempt == 1:
                    print("🎤 Listening... (speak clearly & a bit louder)")
                logger.info(f"Listening attempt {attempt}/{self.max_retries}")
                
                # Re-calibrate briefly on every listen to track noise changes
                # 1.5s gives a good read of the current room noise level
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                print("🔄 Processing...")
                logger.info("Audio captured, sending for recognition...")
                
                # Google STT — best accuracy, handles accents well (en-IN)
                text = self.recognizer.recognize_google(audio, language=self.language)
                
                logger.info(f"Recognized (attempt {attempt}): {text}")
                print(f"👤 You said: '{text}'")
                return text.lower()

        except sr.WaitTimeoutError:
            # No speech detected within timeout — don't retry, just return None
            logger.warning("Listening timed out (no speech detected)")
            print("⏱️ No speech detected. Please try again.")
            return None  # Don't retry on timeout — user simply didn't speak

        except sr.UnknownValueError:
            # Heard noise/audio but couldn't make sense of it
            logger.warning(f"Could not understand audio (attempt {attempt})")
            if attempt == 1:
                print("❓ Couldn't catch that — background noise may be too high.")
            return None  # Will be retried by listen()

        except sr.RequestError as e:
            logger.error(f"Google STT API error: {e}")
            print(f"❌ Speech recognition service error: {e}")
            return None  # Network error — no point retrying immediately

        except Exception as e:
            logger.error(f"Unexpected listen error: {e}")
            print(f"❌ Error during listening: {e}")
            return None

    def test_microphone(self):
        """Test if microphone is working and show current noise level"""
        try:
            with sr.Microphone() as source:
                print("🎤 Testing microphone (2 second noise calibration)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"✅ Microphone is working!")
                print(f"   📊 Current energy threshold: "
                      f"{int(self.recognizer.energy_threshold)} "
                      f"(higher = needs louder speech)")
                logger.info(
                    f"Microphone test OK — "
                    f"energy_threshold={self.recognizer.energy_threshold:.0f}"
                )
                return True
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            logger.error(f"Microphone test failed: {e}")
            return False