"""
AI Router Module
================
Routes AI requests with Gemini as primary and Ollama (phi3) as fallback.

Public functions:
    ask_gemini(prompt: str) -> str
    ask_ollama(prompt: str) -> str
    ask_ai(prompt: str, task_type: str) -> str
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

import requests

from src.ai.ai_config import config
from src.ai.utils.gemini_client import GeminiClient
from src.core.logger import setup_logger

logger = setup_logger(__name__)

_LAST_AI_PROVIDER = "none"

_OLLAMA_URL = getattr(config, "OLLAMA_URL", "http://localhost:11434/api/generate")
_OLLAMA_MODEL = getattr(config, "OLLAMA_MODEL", "phi3")
_DEFAULT_TIMEOUT = max(5, int(getattr(config, "ANALYSIS_TIMEOUT", 30)))
_OLLAMA_TIMEOUT = max(30, int(getattr(config, "OLLAMA_TIMEOUT_SECONDS", 300)))
_SECURITY_FALLBACK_WARNING = (
    "[Fallback Warning] This response is generated using a local model and may not be fully accurate "
    "for security analysis.\n\n"
)


def ask_gemini(prompt: str) -> str:
    """
    Call Gemini API and return response text.

    Returns empty string on timeout, errors, or invalid/empty response.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        logger.warning("ask_gemini received empty prompt")
        return ""

    gemini_keys = config.get_gemini_api_keys()
    if not gemini_keys:
        logger.warning("No valid Gemini API keys configured")
        return ""

    for idx, api_key in enumerate(gemini_keys, start=1):
        def _call_gemini_with_key(current_key=api_key) -> str:
            client = GeminiClient(api_key=current_key)
            return client.generate_text(prompt)

        try:
            logger.info(f"Trying Gemini with key #{idx}")
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_call_gemini_with_key)
                response = future.result(timeout=_DEFAULT_TIMEOUT)

            if response and str(response).strip():
                if idx > 1:
                    logger.warning(f"Gemini succeeded with backup key #{idx - 1}")
                return str(response).strip()

            logger.warning(f"Gemini key #{idx} returned empty response")

        except FutureTimeoutError:
            logger.error(f"Gemini key #{idx} timed out")
        except Exception as exc:
            logger.error(f"Gemini key #{idx} failed: {exc}")

    logger.error("All Gemini API keys failed")
    return ""


def ask_ollama(prompt: str, concise: bool = False) -> str:
    """
    Call local Ollama API (phi3) and return response text.

    Args:
        prompt: The prompt to send to Ollama
        concise: If True, ask Ollama to limit response to 2-3 lines for faster response

    Returns empty string on connection errors, timeouts, invalid responses,
    or empty model output.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        logger.warning("ask_ollama received empty prompt")
        return ""

    # Prepend concise instruction if requested
    final_prompt = prompt
    if concise:
        final_prompt = "[IMPORTANT: Keep your response to MAXIMUM 2-3 lines. Be brief and concise.]\n\n" + prompt

    payload = {
        "model": _OLLAMA_MODEL,
        "prompt": final_prompt,
        "stream": False,
    }

    try:
        response = requests.post(_OLLAMA_URL, json=payload, timeout=_OLLAMA_TIMEOUT)
        response.raise_for_status()

        data = response.json()
        text = data.get("response", "")
        if not text or not str(text).strip():
            logger.warning("Ollama returned an empty or invalid response body")
            return ""

        return str(text).strip()

    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        return ""
    except requests.exceptions.ConnectionError as exc:
        logger.error(f"Ollama connection failed: {exc}")
        return ""
    except requests.exceptions.RequestException as exc:
        logger.error(f"Ollama request failed: {exc}")
        return ""
    except ValueError as exc:
        logger.error(f"Ollama returned invalid JSON: {exc}")
        return ""
    except Exception as exc:
        logger.error(f"Unexpected Ollama error: {exc}")
        return ""


def ask_ai(prompt: str, task_type: str, concise: bool = False) -> str:
    """
    Main AI routing function.

    Args:
        prompt: The prompt to send to AI
        task_type: Type of task ('analysis', 'summary', 'security', etc.)
        concise: If True, request brief 2-3 line responses from fallback (Ollama) for faster processing

    Logic:
    - Always try Gemini first.
    - If Gemini fails/timeout/empty, fallback to Ollama.
    - Add explicit warning for security tasks when fallback is used.
    - When concise=True, Ollama is instructed to limit response to 2-3 lines.
    """
    task_type_normalized = (task_type or "").strip().lower()
    global _LAST_AI_PROVIDER

    print("Using Gemini")
    gemini_response = ask_gemini(prompt)
    if gemini_response:
        _LAST_AI_PROVIDER = "gemini"
        return gemini_response

    logger.warning("Gemini failed, switching to Ollama")
    print("Gemini failed, switching to Ollama")
    print("Fallback to Ollama")

    # Pass concise flag to Ollama for faster response times
    ollama_response = ask_ollama(prompt, concise=concise)
    if not ollama_response:
        _LAST_AI_PROVIDER = "none"
        return (
            "AI service temporarily unavailable. Both Gemini and local Ollama failed "
            "to return a response."
        )

    _LAST_AI_PROVIDER = "ollama"

    if task_type_normalized == "security":
        return _SECURITY_FALLBACK_WARNING + ollama_response

    return ollama_response


def get_last_ai_provider() -> str:
    """Return the provider used by the most recent ask_ai call."""
    return _LAST_AI_PROVIDER
