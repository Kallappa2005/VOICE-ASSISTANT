"""
AI Configuration Module - Using Google Gemini (FREE)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class AIConfig:
    """AI Configuration Manager"""
    
    # ==================== GEMINI SETTINGS (FREE) ====================
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_API_KEY_BACKUP1 = os.getenv('GEMINI_API_KEY_BACKUP1', '')
    GEMINI_API_KEY_BACKUP2 = os.getenv('GEMINI_API_KEY_BACKUP2', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Generation Settings
    MAX_OUTPUT_TOKENS = int(os.getenv('MAX_OUTPUT_TOKENS', 2000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
    
    # Feature Flags
    ENABLE_AI_FEATURES = os.getenv('ENABLE_AI_FEATURES', 'true').lower() == 'true'
    ENABLE_WEBPAGE_ANALYSIS = os.getenv('ENABLE_WEBPAGE_ANALYSIS', 'true').lower() == 'true'
    ENABLE_CODE_ANALYSIS = os.getenv('ENABLE_CODE_ANALYSIS', 'true').lower() == 'true'
    
    # Analysis Settings
    MAX_WEBPAGE_LENGTH = int(os.getenv('MAX_WEBPAGE_LENGTH', 50000))
    MAX_CODE_LENGTH = int(os.getenv('MAX_CODE_LENGTH', 10000))
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 30))
    
    # Rate Limits (Gemini Free Tier)
    REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', 15))
    MONTHLY_TOKEN_LIMIT = int(os.getenv('MONTHLY_TOKEN_LIMIT', 1000000))

    # ==================== OLLAMA FALLBACK SETTINGS ====================
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'phi3')
    OLLAMA_TIMEOUT_SECONDS = int(os.getenv('OLLAMA_TIMEOUT_SECONDS', 300))
    
    @classmethod
    def is_configured(cls):
        """Check if AI is properly configured"""
        return len(cls.get_gemini_api_keys()) > 0

    @classmethod
    def get_gemini_api_keys(cls):
        """
        Return ordered Gemini API keys for failover.

        Priority:
            1) GEMINI_API_KEY
            2) GEMINI_API_KEY_BACKUP1
            3) GEMINI_API_KEY_BACKUP2
        """
        keys = [
            cls.GEMINI_API_KEY,
            cls.GEMINI_API_KEY_BACKUP1,
            cls.GEMINI_API_KEY_BACKUP2,
        ]

        valid_keys = []
        seen = set()
        for key in keys:
            normalized = (key or '').strip()
            if not normalized:
                continue
            if not normalized.startswith('AIza'):
                continue
            if normalized in seen:
                continue
            seen.add(normalized)
            valid_keys.append(normalized)

        return valid_keys
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.is_configured():
            raise ValueError(
                "Gemini API key not configured!\n"
                "Please set GEMINI_API_KEY in .env file.\n"
                "Get your FREE key from: https://aistudio.google.com/app/apikey"
            )
        
        if not cls.ENABLE_AI_FEATURES:
            raise ValueError("AI features are disabled in configuration")
        
        return True
    
    @classmethod
    def get_summary(cls):
        """Get configuration summary"""
        return {
            'configured': cls.is_configured(),
            'model': cls.GEMINI_MODEL,
            'gemini_keys_configured': len(cls.get_gemini_api_keys()),
            'max_tokens': cls.MAX_OUTPUT_TOKENS,
            'webpage_analysis': cls.ENABLE_WEBPAGE_ANALYSIS,
            'code_analysis': cls.ENABLE_CODE_ANALYSIS,
            'api_provider': 'Google Gemini (FREE)',
            'rate_limit': f'{cls.REQUESTS_PER_MINUTE} req/min',
            'ollama_model': cls.OLLAMA_MODEL,
            'ollama_timeout_seconds': cls.OLLAMA_TIMEOUT_SECONDS,
        }

# Global config instance
config = AIConfig()