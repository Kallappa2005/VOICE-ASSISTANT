"""
AI Module - Google Gemini Integration
Provides webpage analysis and code analysis features
"""

from src.ai.ai_config import config, AIConfig
from src.ai.utils.gemini_client import GeminiClient
from src.ai.voice_output import VoiceOutput
from src.ai.ai_commands import AICommandHandler

__all__ = ['config', 'AIConfig', 'GeminiClient', 'VoiceOutput', 'AICommandHandler']

# Check if AI is configured
if config.is_configured():
    print("✅ AI Module: Gemini API configured")
else:
    print("⚠️ AI Module: Gemini API not configured (check .env file)")