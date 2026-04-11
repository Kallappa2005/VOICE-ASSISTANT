"""
Production GUI Integration Test
================================
Quick test to verify the production GUI is properly integrated with main_ai.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from src.ui.production_gui import ProductionGUI
        print("  ✅ ProductionGUI")
    except Exception as e:
        print(f"  ❌ ProductionGUI: {e}")
        return False
    
    try:
        from main_ai import AIVoiceAssistant
        print("  ✅ AIVoiceAssistant")
    except Exception as e:
        print(f"  ❌ AIVoiceAssistant: {e}")
        return False
    
    return True


def test_gui_initialization():
    """Test GUI initialization"""
    print("\nTesting GUI initialization...")
    
    try:
        import tkinter as tk
        from src.ui.production_gui import ProductionGUI
        
        root = tk.Tk()
        gui = ProductionGUI(root)
        print("  ✅ GUI created successfully")
        
        # Test basic methods
        gui.add_chat_message("test", "user")
        print("  ✅ add_chat_message() works")
        
        gui.add_chat_info("test info")
        print("  ✅ add_chat_info() works")
        
        gui.set_project_info("test", "test", "test")
        print("  ✅ set_project_info() works")
        
        gui.set_checklist(["item1", "item2"])
        print("  ✅ set_checklist() works")
        
        gui.add_step("test step", "running")
        print("  ✅ add_step() works")
        
        gui.update_progress(1, 5)
        print("  ✅ update_progress() works")
        
        gui.show()
        print("  ✅ show() works")
        
        gui.show_chat_mode()
        print("  ✅ show_chat_mode() works")
        
        gui.show_project_mode()
        print("  ✅ show_project_mode() works")
        
        gui.close()
        print("  ✅ close() works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_callback_system():
    """Test GUI callback system"""
    print("\nTesting callback system...")
    
    try:
        import tkinter as tk
        from src.ui.production_gui import ProductionGUI
        
        root = tk.Tk()
        gui = ProductionGUI(root)
        
        # Test callback with different update types
        callbacks_tested = [
            {"type": "mode_switch", "mode": "project"},
            {"type": "user_input", "message": "test command"},
            {"type": "assistant_response", "message": "test response"},
            {"type": "project_info", "project_name": "test", "framework": "test", "location": "test"},
            {"type": "plan", "message": ["step1", "step2"]},
            {"type": "step_start", "message": "test step"},
            {"type": "step_complete", "message": "test", "status": "success", "step": 1, "total": 5},
            {"type": "success", "message": "test success"},
            {"type": "error", "message": "test error"},
        ]
        
        for callback in callbacks_tested:
            try:
                gui.update_ui(callback)
                update_type = callback.get("type")
                print(f"  ✅ Callback '{update_type}' works")
            except Exception as e:
                print(f"  ❌ Callback failed: {e}")
                return False
        
        gui.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Callback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 PRODUCTION GUI INTEGRATION TEST")
    print("=" * 70)
    
    results = {
        "Import Test": test_imports(),
        "GUI Initialization": test_gui_initialization(),
        "Callback System": test_callback_system(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED - GUI is ready!")
    else:
        print("❌ SOME TESTS FAILED - Please check the errors above")
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
