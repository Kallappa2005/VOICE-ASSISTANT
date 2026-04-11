"""
Google Gemini API Client Wrapper
Handles API calls with error handling and retry logic
"""

import time
import google.generativeai as genai
from src.ai.ai_config import config
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class GeminiClient:
    """Wrapper for Google Gemini API with error handling"""
    
    def __init__(self, api_key=None):
        """
        Initialize Gemini client.

        Args:
            api_key: Optional API key override (used by router failover)
        """
        if not config.is_configured() and not api_key:
            raise ValueError("Gemini API key not configured")

        selected_key = (api_key or config.GEMINI_API_KEY or "").strip()
        if not selected_key:
            raise ValueError("Gemini API key not configured")

        # Configure API
        genai.configure(api_key=selected_key)
        
        # Initialize model
        self.model_name = config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        
        # Generation config
        self.generation_config = {
            'temperature': config.TEMPERATURE,
            'max_output_tokens': config.MAX_OUTPUT_TOKENS,
        }
        
        # Usage tracking
        self.call_count = 0
        self.total_chars = 0
        
        logger.info(f"Gemini client initialized (model: {self.model_name})")
    
    def generate_text(self, prompt, temperature=None, max_tokens=None):
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt text
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            str: AI response text
        """
        try:
            # Update config if overrides provided
            gen_config = self.generation_config.copy()
            if temperature is not None:
                gen_config['temperature'] = temperature
            if max_tokens is not None:
                gen_config['max_output_tokens'] = max_tokens
            
            logger.info(f"Sending request to Gemini (prompt length: {len(prompt)} chars)")
            
            # Make API call
            response = self.model.generate_content(
                prompt,
                generation_config=gen_config
            )
            
            # Extract text
            result = response.text
            
            # Update usage stats
            self.call_count += 1
            self.total_chars += len(prompt) + len(result)
            
            logger.info(f"Response received (length: {len(result)} chars, total calls: {self.call_count})")
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def chat(self, messages):
        """
        Chat-style conversation
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
        
        Returns:
            str: AI response
        """
        try:
            # Start chat session
            chat = self.model.start_chat(history=[])
            
            # Send messages
            for msg in messages:
                if msg['role'] == 'user':
                    response = chat.send_message(msg['content'])
            
            result = response.text
            
            # Update stats
            self.call_count += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise
    
    def analyze_with_context(self, system_prompt, user_prompt):
        """
        Analyze with system context and user prompt
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
        
        Returns:
            str: AI response
        """
        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        return self.generate_text(full_prompt)
    
    def get_usage_stats(self):
        """Get API usage statistics"""
        return {
            'calls': self.call_count,
            'total_chars': self.total_chars,
            'estimated_tokens': self.total_chars // 4,  # Rough estimate
            'remaining_monthly': config.MONTHLY_TOKEN_LIMIT - (self.total_chars // 4)
        }
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = self.generate_text("Say 'Hello! AI is working.'")
            logger.info("✅ Gemini API connection successful")
            return True, response
        except Exception as e:
            logger.error(f"❌ Gemini API connection failed: {e}")
            return False, str(e)