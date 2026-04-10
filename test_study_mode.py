"""
Study Mode Integration Test
============================
Test the Study Mode functionality including:
  1. Config loading
  2. Topic extraction
  3. Command parsing
  4. Integration with voice assistant
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.automation.study_mode import StudyMode
from src.commands.command_parser import CommandParser
from src.core.logger import setup_logger

logger = setup_logger(__name__)


def test_study_mode_class():
    """Test the StudyMode class directly."""
    print("\n" + "=" * 70)
    print("TEST 1: StudyMode Class Direct Test")
    print("=" * 70)
    
    study = StudyMode()
    
    # Validate config
    print("\n📋 Validating config.json...")
    is_valid = study.validate_config()
    
    if is_valid:
        print("✅ Config validation PASSED")
    else:
        print("❌ Config validation FAILED")
        return False
    
    return True


def test_command_parser():
    """Test command parser for Study Mode intent detection."""
    print("\n" + "=" * 70)
    print("TEST 2: Command Parser - Study Mode Intent Detection")
    print("=" * 70)
    
    parser = CommandParser()
    
    test_cases = [
        ("study mode", None, "Default topic"),
        ("study mode python", "python", "Python topic"),
        ("start studying machine learning", "machine learning", "ML topic"),
        ("focus mode web development", "web development", "Web dev topic"),
        ("learning mode data science", "data science", "Data science topic"),
        ("begin studying", None, "No topic"),
    ]
    
    all_passed = True
    for command, expected_topic, description in test_cases:
        result = parser.parse(command)
        
        # Check intent
        if result['intent'] != 'start_study':
            print(f"❌ {description}: Expected intent 'start_study', got '{result['intent']}'")
            all_passed = False
            continue
        
        # Check topic
        actual_topic = result.get('params', {}).get('topic') if result.get('params') else None
        
        if expected_topic is None:
            if actual_topic is None or actual_topic == "":
                print(f"✅ {description}: Topic correctly None/empty → {command}")
            else:
                print(f"❌ {description}: Expected topic None, got '{actual_topic}'")
                all_passed = False
        else:
            if actual_topic == expected_topic:
                print(f"✅ {description}: Topic extracted correctly → '{actual_topic}'")
            else:
                print(f"❌ {description}: Expected '{expected_topic}', got '{actual_topic}'")
                all_passed = False
    
    return all_passed


def test_other_keywords():
    """Test that other keywords still work (no regression)."""
    print("\n" + "=" * 70)
    print("TEST 3: Regression Test - Other Commands Still Work")
    print("=" * 70)
    
    parser = CommandParser()
    
    other_commands = [
        ("start coding", "start_coding", "Coding Mode"),
        ("youtube", "open_youtube", "Open YouTube"),
        ("search for python tutorials", "search", "Search"),
        ("scroll down", "scroll_down", "Scroll Down"),
        ("take screenshot", "screenshot", "Screenshot"),
    ]
    
    all_passed = True
    for command, expected_intent, description in other_commands:
        result = parser.parse(command)
        
        if result['intent'] == expected_intent:
            print(f"✅ {description}: Intent '{expected_intent}' still works")
        else:
            print(f"❌ {description}: Expected '{expected_intent}', got '{result['intent']}'")
            all_passed = False
    
    return all_passed


def test_topic_variations():
    """Test various topic formats and edge cases."""
    print("\n" + "=" * 70)
    print("TEST 4: Topic Extraction Variations")
    print("=" * 70)
    
    parser = CommandParser()
    
    variations = [
        ("study mode", "", "Single word command"),
        ("study mode react", "react", "Single topic word"),
        ("study mode react hooks", "react hooks", "Multi-word topic"),
        ("study mode javascript advanced concepts", "javascript advanced concepts", "Long topic"),
        ("start studying python for beginners", "python for beginners", "Complex topic with 'for'"),
    ]
    
    all_passed = True
    for command, expected_topic, description in variations:
        result = parser.parse(command)
        actual_topic = (result.get('params', {}).get('topic') or "").strip() if result.get('params') else ""
        
        if actual_topic == expected_topic:
            print(f"✅ {description}: '{actual_topic}' → Correct")
        else:
            print(f"❌ {description}: Expected '{expected_topic}', got '{actual_topic}'")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "🧪 " + "=" * 65)
    print("🧪  STUDY MODE INTEGRATION TEST SUITE")
    print("🧪 " + "=" * 65)
    
    results = {
        "StudyMode Class": test_study_mode_class(),
        "Command Parser": test_command_parser(),
        "Regression Tests": test_other_keywords(),
        "Topic Variations": test_topic_variations(),
    }
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} → {test_name}")
    
    print("\n" + "=" * 70)
    print(f"🎯 Overall: {passed_count}/{total_count} test groups passed")
    print("=" * 70 + "\n")
    
    return all(results.values())


# ─────────────────────────────────────────────────────────────────────
# Manual Test: Study Mode Simulation
# ─────────────────────────────────────────────────────────────────────

def simulate_voice_command(command_text):
    """Simulate what happens when a voice command is received."""
    print("\n" + "─" * 70)
    print(f"🎤 Voice Command Received: '{command_text}'")
    print("─" * 70)
    
    parser = CommandParser()
    result = parser.parse(command_text)
    
    print(f"🔍 Parsed Intent: {result['intent']}")
    if result.get('params'):
        print(f"📝 Parameters: {result['params']}")
    
    if result['intent'] == 'start_study':
        topic = result.get('params', {}).get('topic')
        topic_str = f"for '{topic}'" if topic else "(no topic)"
        print(f"✅ Would start Study Mode {topic_str}")
        print(f"   Step 1: Mute notifications")
        print(f"   Step 2: Open YouTube search")
        print(f"   Step 3: Open GeeksforGeeks docs")
        print(f"   Step 4: Open Notepad")
    
    return result['intent'] == 'start_study'


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Study Mode integration"
    )
    parser.add_argument(
        "--test",
        choices=["all", "class", "parser", "regression", "variations"],
        default="all",
        help="Which test to run (default: all)"
    )
    parser.add_argument(
        "--simulate",
        type=str,
        help="Simulate a voice command (e.g., 'study mode python')"
    )
    
    args = parser.parse_args()
    
    if args.simulate:
        simulate_voice_command(args.simulate)
    else:
        success = main()
        sys.exit(0 if success else 1)
