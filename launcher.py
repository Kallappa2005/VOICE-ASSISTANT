#!/usr/bin/env python3
"""
Voice Assistant Launcher
Unified entry point for both basic and AI modes with GUI
Supports Docker containerization and Kubernetes deployment

Usage:
    python launcher.py --mode basic     # Run basic assistant with GUI
    python launcher.py --mode ai        # Run AI assistant with GUI
    python launcher.py --help           # Show help
    
Environment variables:
    ASSISTANT_MODE: "basic" or "ai" (default: "ai")
    DOCKER_CONTAINER: "true" or "false" (set by Docker)
    DEBUG: "true" or "false"
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.logger import setup_logger

logger = setup_logger(__name__)


def get_mode_from_env():
    """Get assistant mode from environment variables"""
    mode = os.getenv("ASSISTANT_MODE", "ai").lower()
    if mode not in ["basic", "ai"]:
        logger.warning(f"Invalid mode: {mode}, defaulting to ai")
        mode = "ai"
    return mode


def run_basic_assistant_with_gui():
    """Run basic voice assistant with GUI"""
    logger.info("Starting Basic Voice Assistant with GUI...")
    
    from main import VoiceAssistant
    
    # Create assistant (will auto-create GUI)
    assistant = VoiceAssistant()
    
    # Start the assistant (handles GUI threading internally)
    try:
        assistant.start()
    except Exception as e:
        logger.error(f"Assistant error: {e}", exc_info=True)
        raise


def run_ai_assistant_with_gui():
    """Run AI voice assistant with GUI"""
    logger.info("Starting AI Voice Assistant with GUI...")
    
    from main_ai import AIVoiceAssistant
    
    # Create assistant (will auto-create GUI)
    assistant = AIVoiceAssistant()
    
    # Start the assistant (handles GUI threading internally)
    try:
        assistant.start()
    except Exception as e:
        logger.error(f"Assistant error: {e}", exc_info=True)
        raise


def run_basic_assistant_headless():
    """Run basic assistant without GUI (for servers/containers)"""
    logger.info("Starting Basic Voice Assistant (Headless)...")
    
    from main import VoiceAssistant
    
    assistant = VoiceAssistant()
    assistant.start()


def run_ai_assistant_headless():
    """Run AI assistant without GUI (for servers/containers)"""
    logger.info("Starting AI Voice Assistant (Headless)...")
    
    from main_ai import AIVoiceAssistant
    
    assistant = AIVoiceAssistant()
    assistant.start()


def main():
    """Main launcher"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Voice Assistant Launcher",
        epilog="Examples:\n"
               "  python launcher.py --mode ai\n"
               "  python launcher.py --mode basic --no-gui\n"
               "  ASSISTANT_MODE=basic python launcher.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--mode",
        choices=["basic", "ai"],
        default=None,
        help="Assistant mode (default: from env or 'ai')",
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (headless mode)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug or os.getenv("DEBUG", "").lower() == "true":
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Get mode
    mode = args.mode or get_mode_from_env()
    
    # Print startup info
    print("\n" + "=" * 80)
    print("🤖 VOICE ASSISTANT LAUNCHER")
    print("=" * 80)
    print(f"Mode: {mode}")
    print(f"GUI: {'Disabled' if args.no_gui else 'Enabled'}")
    print(f"Debug: {'Enabled' if (args.debug or os.getenv('DEBUG')) else 'Disabled'}")
    print("=" * 80 + "\n")
    
    # Run appropriate assistant
    try:
        if args.no_gui:
            if mode == "basic":
                run_basic_assistant_headless()
            else:
                run_ai_assistant_headless()
        else:
            if mode == "basic":
                run_basic_assistant_with_gui()
            else:
                run_ai_assistant_with_gui()
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\n👋 Goodbye!\n")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
