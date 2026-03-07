"""
Test Webpage Analyzer
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai.analyzers.webpage_analyzer import WebPageAnalyzer

def test_webpage_analyzer():
    print("\n" + "=" * 70)
    print("🧪 TESTING WEBPAGE ANALYZER")
    print("=" * 70)
    
    analyzer = WebPageAnalyzer()
    
    # Test 1: Summarize a webpage
    print("\n1️⃣ Test: Summarize Wikipedia Page")
    print("-" * 70)
    
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    result = analyzer.summarize_url(url, summary_type='tldr')
    
    if result['success']:
        print(f"✅ Success!")
        print(f"\n📄 Title: {result['title']}")
        print(f"\n📝 Summary:\n{result['summary']}")
        print(f"\n📊 Content Length: {result['content_length']} chars")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_webpage_analyzer()