"""
Test Code Analyzer
"""

import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.ai.analyzers.code_analyzer import CodeAnalyzer

def test_code_analyzer():
    print("\n" + "=" * 70)
    print("🧪 TESTING CODE ANALYZER")
    print("=" * 70)
    
    analyzer = CodeAnalyzer()
    
    # Test code with SQL injection vulnerability
    vulnerable_code = """
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Vulnerable to SQL injection!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchone()

def search_products(search_term):
    query = "SELECT * FROM products WHERE name LIKE '%" + search_term + "%'"
    return execute_query(query)
"""
    
    print("\n1️⃣ Test: Security Analysis (SQL Injection Detection)")
    print("-" * 70)
    
    result = analyzer.analyze_code(vulnerable_code, language='python', analysis_type='security')
    
    if result['success']:
        print(f"✅ Analysis Complete!")
        print(f"\n🔒 Security Issues Found:")
        print(f"   • SQL Injection: {result['security']['sql_injection_found']}")
        print(f"   • XSS: {result['security']['xss_found']}")
        print(f"   • Total: {result['security']['total_vulnerabilities']}")
        
        if result['security']['vulnerabilities']:
            print(f"\n⚠️ Vulnerabilities:")
            for vuln in result['security']['vulnerabilities']:
                print(f"\n   Line {vuln['line']}: {vuln['type']} [{vuln['severity']}]")
                print(f"   Code: {vuln['code']}")
                print(f"   {vuln['description']}")
        
        print(f"\n🤖 AI Analysis:\n{result['ai_analysis'][:500]}...")
        
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_code_analyzer()