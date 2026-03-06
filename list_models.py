"""
List Available Gemini Models
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Configure API
genai.configure(api_key=api_key)

print("\n" + "=" * 70)
print("📋 AVAILABLE GEMINI MODELS")
print("=" * 70)

# List all models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✅ Model: {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print(f"   Supported Methods: {', '.join(model.supported_generation_methods)}")

print("\n" + "=" * 70)
print("💡 Use these model names in your .env file")
print("   Example: GEMINI_MODEL=gemini-1.5-flash-latest")
print("=" * 70 + "\n")