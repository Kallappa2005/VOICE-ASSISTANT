"""
Test script for Ollama phi3 model
================================
This script tests whether Ollama phi3 model is working correctly
by sending a simple prompt and checking the response.

Usage:
    python tests/test_ollama.py

Requirements:
    - Ollama service running at http://localhost:11434
    - phi3 model installed in Ollama
"""

import requests
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import setup_logger

logger = setup_logger(__name__)

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3"
TIMEOUT = 300  # 5 minutes for slower systems


def test_ollama_connection():
    """Test if Ollama service is reachable"""
    print("[1/3] Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        print("✓ Ollama service is reachable")
        return True
    except requests.exceptions.ConnectionError:
        print(
            "✗ Connection failed: Ollama service not running at http://localhost:11434"
        )
        print("   Make sure Ollama is started: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        return False


def test_ollama_model_available():
    """Check if phi3 model is available"""
    print("\n[2/3] Checking if phi3 model is installed...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])

        available_models = [m.get("name", "").split(":")[0] for m in models]

        if "phi3" in available_models or any("phi" in m for m in available_models):
            print(f"✓ phi3 model is installed")
            print(f"  Available models: {', '.join(available_models)}")
            return True
        else:
            print(f"✗ phi3 model not found")
            print(f"  Available models: {', '.join(available_models)}")
            print("  Install phi3: ollama pull phi3")
            return False

    except Exception as e:
        print(f"✗ Failed to check models: {e}")
        return False


def test_ollama_prompt():
    """Send a simple prompt to Ollama and check response"""
    print("\n[3/3] Testing prompt response...")

    prompt = "hi how are you!"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    print(f"  Sending prompt: '{prompt}'")
    print(f"  Timeout: {TIMEOUT} seconds")
    print("  Waiting for response (this may take a minute on limited hardware)...\n")

    try:
        start_time = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        end_time = time.time()
        elapsed_time = end_time - start_time

        response.raise_for_status()
        data = response.json()

        generated_text = data.get("response", "")

        if not generated_text or not str(generated_text).strip():
            print("✗ Ollama returned empty response")
            return False

        print(f"✓ Response received in {elapsed_time:.1f} seconds")
        print(f"\n--- Ollama Response ---")
        print(generated_text)
        print(f"--- End Response ---\n")

        # Check response quality
        response_len = len(generated_text.strip())
        if response_len < 10:
            print("⚠ Warning: Response is very short (might be truncated)")
            return False

        print("\n✓ Ollama phi3 model is working correctly!")
        return True

    except requests.exceptions.Timeout:
        print(f"✗ Request timed out after {TIMEOUT} seconds")
        print("  This usually means:")
        print("  - phi3 model is still loading (takes 30-60s first time)")
        print("  - System hardware is very limited")
        print("  - Try increasing OLLAMA_TIMEOUT_SECONDS in .env")
        return False

    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print(f"  Ollama URL: {OLLAMA_URL}")
        return False

    except Exception as e:
        print(f"✗ Test failed: {e}")
        logger.error(f"Ollama test error: {e}", exc_info=True)
        return False


def main():
    """Run all Ollama tests"""
    print("=" * 60)
    print("Ollama phi3 Model Test")
    print("=" * 60)

    results = []

    # Test 1: Connection
    if not test_ollama_connection():
        print("\n" + "=" * 60)
        print("❌ Test Failed: Cannot connect to Ollama")
        print("=" * 60)
        return 1

    results.append(True)

    # Test 2: Model availability
    if not test_ollama_model_available():
        print("\n" + "=" * 60)
        print("⚠️ Test Warning: phi3 model not installed")
        print("=" * 60)
        return 1

    results.append(True)

    # Test 3: Prompt response
    if not test_ollama_prompt():
        print("\n" + "=" * 60)
        print("❌ Test Failed: Could not get valid response")
        print("=" * 60)
        return 1

    results.append(True)

    # All tests passed
    print("=" * 60)
    print("✅ All Tests Passed!")
    print("Ollama phi3 model is ready for use")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
