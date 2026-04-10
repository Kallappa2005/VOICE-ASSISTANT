"""
PHASE 1: Verification Test
Tests that all new modules import correctly without errors
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all new modules import successfully"""
    print("\n" + "=" * 70)
    print("PHASE 1: IMPORT VERIFICATION")
    print("=" * 70 + "\n")
    
    errors = []
    
    # Test 1: Voice module
    print("1. Testing VoiceInput...")
    try:
        from src.voice.voice import VoiceInput
        print("   ✓ VoiceInput imported successfully")
    except Exception as e:
        print(f"   ✗ VoiceInput import failed: {e}")
        errors.append(f"VoiceInput: {e}")
    
    # Test 2: Assistant module
    print("2. Testing Assistant...")
    try:
        from src.assistant import Assistant
        print("   ✓ Assistant imported successfully")
    except Exception as e:
        print(f"   ✗ Assistant import failed: {e}")
        errors.append(f"Assistant: {e}")
    
    # Test 3: UI Handler
    print("3. Testing UIHandler...")
    try:
        from src.ui.simple_ui import UIHandler
        print("   ✓ UIHandler imported successfully")
    except Exception as e:
        print(f"   ✗ UIHandler import failed: {e}")
        errors.append(f"UIHandler: {e}")
    
    # Test 4: ExecutionManager with ui_callback
    print("4. Testing ExecutionManager...")
    try:
        from src.agent.execution_manager import ExecutionManager
        print("   ✓ ExecutionManager imported successfully")
    except Exception as e:
        print(f"   ✗ ExecutionManager import failed: {e}")
        errors.append(f"ExecutionManager: {e}")
    
    # Test 5: All existing modules still work
    print("5. Testing existing modules...")
    try:
        from src.speech.text_to_speech_handler import TextToSpeechHandler
        from src.speech.speech_recognition_handler import SpeechRecognitionHandler
        from src.commands.command_parser import CommandParser
        from src.browser.browser_controller import BrowserController
        print("   ✓ All existing modules imported successfully")
    except Exception as e:
        print(f"   ✗ Existing module import failed: {e}")
        errors.append(f"Existing modules: {e}")
    
    # Results
    print("\n" + "=" * 70)
    if errors:
        print(f"❌ FAILED: {len(errors)} error(s) found:\n")
        for error in errors:
            print(f"  • {error}")
        print("\n" + "=" * 70)
        return False
    else:
        print("✓ SUCCESS: All modules import correctly!")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
