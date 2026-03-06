"""
AI Module - Google Gemini Integration
Provides webpage analysis and code analysis features
"""

from src.ai.ai_config import config, AIConfig
from src.ai.utils.gemini_client import GeminiClient

__all__ = ['config', 'AIConfig', 'GeminiClient']

# Check if AI is configured
if config.is_configured():
    print("✅ AI Module: Gemini API configured")
else:
    print("⚠️ AI Module: Gemini API not configured (check .env file)")