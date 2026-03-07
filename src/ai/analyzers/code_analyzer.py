"""
Code Analyzer
Analyzes code for security, complexity, and quality using Gemini AI
"""

import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from src.ai.utils.gemini_client import GeminiClient
from src.ai.ai_config import config
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class CodeAnalyzer:
    """Analyze code for security, complexity, and quality"""
    
    def __init__(self, gemini_client):
        """Initialize code analyzer"""
        self.client = gemini_client
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            r"execute\s*\(\s*['\"].*\+.*['\"]",  # String concatenation in execute
            r"SELECT.*\+.*FROM",  # SQL with string concat
            r"query\s*=\s*['\"].*%s.*['\"]",  # String formatting
            r"query\s*=\s*f['\"].*\{.*\}.*['\"]",  # f-string in SQL
            r"\.format\(.*\).*execute",  # .format() with execute
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"innerHTML\s*=",  # Direct innerHTML assignment
            r"document\.write\(",  # document.write
            r"eval\(",  # eval usage
            r"dangerouslySetInnerHTML",  # React dangerous HTML
        ]
        
        logger.info("Code analyzer initialized")
    
    def detect_sql_injection(self, code):
        """
        Detect potential SQL injection vulnerabilities
        
        Args:
            code: Code string to analyze
        
        Returns:
            list: Found vulnerabilities
        """
        vulnerabilities = []
        
        for i, line in enumerate(code.splitlines(), 1):
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'SQL Injection',
                        'severity': 'HIGH',
                        'code': line.strip(),
                        'description': 'Potential SQL injection vulnerability detected'
                    })
        
        return vulnerabilities
    
    def detect_xss(self, code):
        """
        Detect potential XSS vulnerabilities
        
        Args:
            code: Code string to analyze
        
        Returns:
            list: Found vulnerabilities
        """
        vulnerabilities = []
        
        for i, line in enumerate(code.splitlines(), 1):
            for pattern in self.xss_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulnerabilities.append({
                        'line': i,
                        'type': 'XSS (Cross-Site Scripting)',
                        'severity': 'HIGH',
                        'code': line.strip(),
                        'description': 'Potential XSS vulnerability detected'
                    })
        
        return vulnerabilities
    
    def calculate_complexity(self, code):
        """
        Calculate code complexity metrics
        
        Args:
            code: Python code string
        
        Returns:
            dict: Complexity metrics
        """
        try:
            # Cyclomatic complexity
            complexity = cc_visit(code)
            
            # Maintainability index
            mi = mi_visit(code, multi=True)
            
            avg_complexity = sum(c.complexity for c in complexity) / len(complexity) if complexity else 0
            
            return {
                'average_complexity': round(avg_complexity, 2),
                'total_functions': len(complexity),
                'maintainability_index': round(mi, 2),
                'complexity_grade': self._get_complexity_grade(avg_complexity)
            }
            
        except Exception as e:
            logger.warning(f"Could not calculate complexity: {e}")
            return {
                'average_complexity': 0,
                'total_functions': 0,
                'maintainability_index': 0,
                'complexity_grade': 'Unknown'
            }
    
    def _get_complexity_grade(self, complexity):
        """Get complexity grade"""
        if complexity <= 5:
            return 'A (Simple)'
        elif complexity <= 10:
            return 'B (Moderate)'
        elif complexity <= 20:
            return 'C (Complex)'
        elif complexity <= 30:
            return 'D (Very Complex)'
        else:
            return 'F (Extremely Complex)'
    
    def analyze_code(self, code, language='python', analysis_type='full'):
        """
        Comprehensive code analysis
        
        Args:
            code: Code string to analyze
            language: Programming language
            analysis_type: 'full', 'security', 'complexity', 'quality'
        
        Returns:
            dict: Analysis results
        """
        try:
            logger.info(f"Analyzing {language} code ({len(code)} chars)...")
            
            results = {
                'success': True,
                'language': language,
                'code_length': len(code),
                'analysis_type': analysis_type
            }
            
            # Security analysis
            if analysis_type in ['full', 'security']:
                sql_vulns = self.detect_sql_injection(code)
                xss_vulns = self.detect_xss(code)
                
                results['security'] = {
                    'sql_injection_found': len(sql_vulns),
                    'xss_found': len(xss_vulns),
                    'total_vulnerabilities': len(sql_vulns) + len(xss_vulns),
                    'vulnerabilities': sql_vulns + xss_vulns
                }
            
            # Complexity analysis (Python only)
            if analysis_type in ['full', 'complexity'] and language.lower() == 'python':
                results['complexity'] = self.calculate_complexity(code)
            
            # AI-powered analysis
            if analysis_type in ['full', 'quality', 'security']:
                ai_analysis = self._get_ai_analysis(code, language, analysis_type)
                results['ai_analysis'] = ai_analysis
            
            results['usage'] = self.client.get_usage_stats()
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_ai_analysis(self, code, language, analysis_type):
        """
        Get AI-powered code analysis
        
        Args:
            code: Code to analyze
            language: Programming language
            analysis_type: Type of analysis
        
        Returns:
            str: AI analysis
        """
        prompts = {
            'security': f"""Analyze this {language} code for security vulnerabilities.

Code:
```{language}
{code}
```

Identify:
1. SQL Injection vulnerabilities
2. XSS (Cross-Site Scripting) vulnerabilities
3. Authentication/Authorization issues
4. Input validation problems
5. Other security concerns

For each vulnerability, provide:
- Severity (HIGH/MEDIUM/LOW)
- Line numbers (if applicable)
- Description
- Fix recommendation""",

            'complexity': f"""Analyze this {language} code for complexity and maintainability.

Code:
```{language}
{code}
```

Evaluate:
1. Code complexity
2. Readability
3. Maintainability
4. Best practices adherence
5. Suggestions for improvement""",

            'quality': f"""Review this {language} code for overall quality.

Code:
```{language}
{code}
```

Assess:
1. Code quality
2. Design patterns
3. Error handling
4. Documentation
5. Performance concerns
6. Refactoring suggestions""",

            'full': f"""Perform a comprehensive analysis of this {language} code.

Code:
```{language}
{code}
```

Provide:
1. **Security Analysis** - Vulnerabilities (SQL injection, XSS, etc.)
2. **Complexity** - Code complexity and maintainability
3. **Quality** - Overall code quality and best practices
4. **Bugs** - Potential bugs or logic errors
5. **Recommendations** - Specific improvement suggestions"""
        }
        
        prompt = prompts.get(analysis_type, prompts['full'])
        
        logger.info(f"Getting AI analysis ({analysis_type})...")
        
        return self.client.generate_text(prompt, max_tokens=3000)
    
    def find_bugs(self, code, language='python'):
        """
        Find potential bugs in code
        
        Args:
            code: Code to analyze
            language: Programming language
        
        Returns:
            dict: Bug analysis
        """
        try:
            prompt = f"""Analyze this {language} code for bugs and logic errors.

Code:
```{language}
{code}
```

Find:
1. Logic errors
2. Potential runtime errors
3. Edge case handling issues
4. Resource leaks
5. Infinite loops

For each issue:
- Severity
- Description
- Location
- Fix suggestion"""

            logger.info("Analyzing code for bugs...")
            
            analysis = self.client.generate_text(prompt, max_tokens=2000)
            
            return {
                'success': True,
                'language': language,
                'bug_analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error finding bugs: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_improvements(self, code, language='python'):
        """
        Suggest code improvements
        
        Args:
            code: Code to improve
            language: Programming language
        
        Returns:
            dict: Improvement suggestions
        """
        try:
            prompt = f"""Suggest improvements for this {language} code.

Code:
```{language}
{code}
```

Provide:
1. Refactoring suggestions
2. Performance optimizations
3. Better design patterns
4. Code simplification
5. Modern best practices

For each suggestion, show before/after code if applicable."""

            logger.info("Generating improvement suggestions...")
            
            suggestions = self.client.generate_text(prompt, max_tokens=2500)
            
            return {
                'success': True,
                'language': language,
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_file(self, file_path):
        """
        Analyze code file for security vulnerabilities
        
        Args:
            file_path: Path to code file
        
        Returns:
            dict: Analysis results with vulnerabilities and AI analysis
        """
        try:
            import os
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return {
                    'error': f"File not found: {file_path}"
                }
            
            # Read file
            logger.info(f"Reading file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Detect language from file extension
            file_name = os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()
            
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
                '.cs': 'csharp',
                '.php': 'php',
                '.rb': 'ruby',
                '.go': 'go'
            }
            
            language = language_map.get(ext, 'python')
            logger.info(f"Detected language: {language}")
            
            # Analyze code (use 'full' to get complexity + security + AI analysis)
            analysis = self.analyze_code(code, language=language, analysis_type='full')
            
            if not analysis.get('success'):
                return {
                    'error': analysis.get('error', 'Analysis failed')
                }
            
            # Format results for ai_commands.py
            security = analysis.get('security', {})
            vulnerabilities = security.get('vulnerabilities', [])
            complexity = analysis.get('complexity', {})
            
            result = {
                'file_name': file_name,
                'language': language,
                'code_length': len(code),
                'sql_injection_count': security.get('sql_injection_found', 0),
                'xss_count': security.get('xss_found', 0),
                'total_vulnerabilities': security.get('total_vulnerabilities', 0),
                'vulnerabilities': vulnerabilities,
                'complexity': complexity,  # Added complexity metrics
                'ai_analysis': analysis.get('ai_analysis', '')
            }
            
            logger.info(f"File analysis complete: {file_name} ({result['total_vulnerabilities']} issues)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {
                'error': f"Error reading or analyzing file: {str(e)}"
            }
    
    def analyze_clipboard(self):
        """
        Analyze code from clipboard
        
        Returns:
            dict: Analysis results with vulnerabilities
        """
        try:
            import pyperclip
            
            # Get clipboard content
            logger.info("Reading clipboard...")
            code = pyperclip.paste()
            
            if not code or len(code.strip()) < 10:
                logger.error("No code found in clipboard")
                return {
                    'error': "No code found in clipboard or code is too short"
                }
            
            logger.info(f"Clipboard content length: {len(code)} characters")
            
            # Try to detect language (Python default)
            language = 'python'
            if 'function' in code and '{' in code:
                language = 'javascript'
            elif 'public class' in code or 'public static' in code:
                language = 'java'
            
            logger.info(f"Analyzing as {language} code...")
            
            # Analyze code
            analysis = self.analyze_code(code, language=language, analysis_type='security')
            
            if not analysis.get('success'):
                return {
                    'error': analysis.get('error', 'Analysis failed')
                }
            
            # Format results for ai_commands.py
            security = analysis.get('security', {})
            vulnerabilities = security.get('vulnerabilities', [])
            
            result = {
                'code_length': len(code),
                'total_vulnerabilities': security.get('total_vulnerabilities', 0),
                'vulnerabilities': vulnerabilities,
                'ai_analysis': analysis.get('ai_analysis', '')
            }
            
            logger.info(f"Clipboard analysis complete ({result['total_vulnerabilities']} issues)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing clipboard: {e}")
            return {
                'error': f"Error analyzing clipboard: {str(e)}"
            }