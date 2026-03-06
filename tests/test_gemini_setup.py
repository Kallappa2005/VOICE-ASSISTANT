"""
Test Gemini API Setup
Run this to verify your configuration works
"""

import sys
import os

# Add parent directory (project root) to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from src.ai.ai_config import config
from src.ai.utils.gemini_client import GeminiClient

def test_setup():
    """Test Gemini API setup"""
    
    print("\n" + "=" * 60)
    print("🧪 TESTING GEMINI API SETUP")
    print("=" * 60)
    
    # Test 1: Check configuration
    print("\n1️⃣ Testing Configuration...")
    try:
        config.validate()
        print("   ✅ Configuration valid")
        
        summary = config.get_summary()
        print(f"\n   📊 Config Summary:")
        print(f"   • API Provider: {summary['api_provider']}")
        print(f"   • Model: {summary['model']}")
        print(f"   • Max Tokens: {summary['max_tokens']}")
        print(f"   • Rate Limit: {summary['rate_limit']}")
        print(f"   • Webpage Analysis: {'✅' if summary['webpage_analysis'] else '❌'}")
        print(f"   • Code Analysis: {'✅' if summary['code_analysis'] else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Initialize client
    print("\n2️⃣ Testing Gemini Client...")
    try:
        client = GeminiClient()
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"   ❌ Client initialization error: {e}")
        return False
    
    # Test 3: Test API connection
    print("\n3️⃣ Testing API Connection...")
    try:
        success, response = client.test_connection()
        if success:
            print(f"   ✅ API connection successful")
            print(f"   📝 Response: {response}")
        else:
            print(f"   ❌ API connection failed: {response}")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 4: Simple prompt
    print("\n4️⃣ Testing Simple Prompt...")
    try:
        prompt = "Explain what SQL injection is in one sentence."
        response = client.generate_text(prompt)
        print(f"   ✅ Prompt successful")
        print(f"   📝 Response: {response[:100]}...")
    except Exception as e:
        print(f"   ❌ Prompt error: {e}")
        return False
    
    # Test 5: Usage stats
    print("\n5️⃣ Checking Usage Stats...")
    stats = client.get_usage_stats()
    print(f"   • Total Calls: {stats['calls']}")
    print(f"   • Estimated Tokens Used: {stats['estimated_tokens']}")
    print(f"   • Remaining Monthly: {stats['remaining_monthly']:,}")
    
    # Success!
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Gemini API is ready!")
    print("=" * 60)
    print("\n🚀 You can now build the analyzers!")
    print("\n")
    
    return True

if __name__ == "__main__":
    try:
        test_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")