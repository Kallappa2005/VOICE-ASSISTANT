"""
AI Command Handler
Handles AI-powered features (webpage analysis, code analysis)
"""

from src.core.logger import setup_logger
from src.ai.utils.gemini_client import GeminiClient
from src.ai.utils.ai_router import get_last_ai_provider
from src.ai.analyzers.webpage_analyzer import WebpageAnalyzer
from src.ai.analyzers.code_analyzer import CodeAnalyzer
from src.ai.voice_output import VoiceOutput

logger = setup_logger(__name__)

class AICommandHandler:
    """Handle AI-powered commands"""
    
    def __init__(self, browser_controller):
        """
        Initialize AI command handler
        
        Args:
            browser_controller: BrowserController instance
        """
        self.browser = browser_controller
        
        # Initialize Gemini client (best effort; router can still fallback to Ollama)
        gemini_client = None
        try:
            gemini_client = GeminiClient()
        except Exception as e:
            logger.warning(f"Gemini client init failed; fallback-only mode active: {e}")
        
        # Initialize analyzers
        self.webpage_analyzer = WebpageAnalyzer(gemini_client)
        self.code_analyzer = CodeAnalyzer(gemini_client)
        
        # Initialize voice output
        self.voice_output = VoiceOutput()
        
        logger.info("AI Command Handler initialized")
    
    def analyze_current_page(self):
        """
        Analyze the currently open webpage
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Analyzing current page...")
            
            # Check if browser is open
            if not self.browser.is_open():
                logger.error("Browser is not open")
                self.voice_output.speak("Browser is not open.")
                return False
            
            # Get driver
            driver = self.browser.get_driver()
            
            # Extract content
            logger.info("Extracting page content...")
            content_data = self.webpage_analyzer.extract_content(driver)
            
            # Validate content
            if content_data['content_length'] < 100:
                logger.warning("Insufficient content for analysis")
                self.voice_output.speak("Could not extract enough content from the page.")
                return False
            
            # Analyze with AI
            logger.info("Sending to AI for analysis...")
            analysis = self.webpage_analyzer.analyze_page(content_data)

            if get_last_ai_provider() == 'ollama':
                self.voice_output.speak("Gemini API failed. Using local Ollama backup.")
            
            # Display results
            print("\n" + "="*70)
            print("📄 PAGE ANALYSIS")
            print("="*70)
            print(f"\n📌 Title: {content_data['title']}")
            print(f"🔗 URL: {content_data['url']}")
            print(f"\n{analysis}")
            print("\n" + "="*70)
            
            # Speak summary
            summary = self._extract_first_sentences(analysis, max_sentences=3)
            self.voice_output.speak(f"Analysis complete. {summary}")
            
            logger.info("Page analysis completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            self.voice_output.speak("An error occurred while analyzing the page.")
            return False
    
    def summarize_page(self):
        """
        Summarize the currently open webpage
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Summarizing current page...")
            
            # Check if browser is open
            if not self.browser.is_open():
                logger.error("Browser is not open")
                self.voice_output.speak("Browser is not open.")
                return False
            
            # Get driver
            driver = self.browser.get_driver()
            
            # Extract content
            logger.info("Extracting page content...")
            content_data = self.webpage_analyzer.extract_content(driver)
            
            # Validate content
            if content_data['content_length'] < 100:
                logger.warning("Insufficient content for summarization")
                self.voice_output.speak("Could not extract enough content from the page.")
                return False
            
            # Summarize with AI
            logger.info("Sending to AI for summarization...")
            summary = self.webpage_analyzer.summarize_page(content_data)

            if get_last_ai_provider() == 'ollama':
                self.voice_output.speak("Gemini API failed. Using local Ollama backup.")
            
            # Display results
            print("\n" + "="*70)
            print("📝 PAGE SUMMARY")
            print("="*70)
            print(f"\n📌 Title: {content_data['title']}")
            print(f"🔗 URL: {content_data['url']}")
            print(f"\n{summary}")
            print("\n" + "="*70)
            
            # Speak summary
            self.voice_output.speak(summary)
            
            logger.info("Page summarization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error summarizing page: {e}")
            self.voice_output.speak("An error occurred while summarizing the page.")
            return False
    
    def get_key_points(self):
        """
        Extract key points from the currently open webpage
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Extracting key points from current page...")
            
            # Check if browser is open
            if not self.browser.is_open():
                logger.error("Browser is not open")
                self.voice_output.speak("Browser is not open.")
                return False
            
            # Get driver
            driver = self.browser.get_driver()
            
            # Extract content
            logger.info("Extracting page content...")
            content_data = self.webpage_analyzer.extract_content(driver)
            
            # Validate content
            if content_data['content_length'] < 100:
                logger.warning("Insufficient content for key points extraction")
                self.voice_output.speak("Could not extract enough content from the page.")
                return False
            
            # Extract key points with AI
            logger.info("Sending to AI for key points extraction...")
            key_points = self.webpage_analyzer.extract_key_points(content_data)

            if get_last_ai_provider() == 'ollama':
                self.voice_output.speak("Gemini API failed. Using local Ollama backup.")
            
            # Display results
            print("\n" + "="*70)
            print("🔑 KEY POINTS")
            print("="*70)
            print(f"\n📌 Title: {content_data['title']}")
            print(f"🔗 URL: {content_data['url']}")
            print()
            
            for i, point in enumerate(key_points, 1):
                print(f"{i}. {point}")
            
            print("\n" + "="*70)
            
            # Speak summary of key points
            num_points = len(key_points)
            if num_points > 0:
                speech = f"Found {num_points} key points. Here are the first few: {'. '.join(key_points[:3])}"
                self.voice_output.speak(speech)
            else:
                self.voice_output.speak("Could not extract key points from the page.")
            
            logger.info(f"Key points extraction completed: {num_points} points found")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            self.voice_output.speak("An error occurred while extracting key points.")
            return False
    
    def analyze_code_file(self, file_path):
        """
        Analyze code file for security vulnerabilities
        
        Args:
            file_path: Path to code file (if empty, uses default test_code.py)
        
        Returns:
            bool: Success status
        """
        try:
            import os
            
            # If no file path provided, use default test_code.py in analyzers folder
            if not file_path or file_path.strip() == '':
                default_file = os.path.join(os.path.dirname(__file__), 'analyzers', 'test_code.py')
                file_path = default_file
                logger.info(f"No file specified, using default: {file_path}")
                print(f"\n📂 Using default test file: test_code.py")
                self.voice_output.speak("Analyzing test code file.")
            
            logger.info(f"Analyzing code file: {file_path}")
            
            # Analyze file
            result = self.code_analyzer.analyze_file(file_path)
            
            if result.get('error'):
                logger.error(f"Code analysis error: {result['error']}")
                self.voice_output.speak(result['error'])
                return False
            
            # Display results
            print("\n" + "="*70)
            print("💻 CODE ANALYSIS RESULTS")
            print("="*70)
            print(f"\n📄 File: {result['file_name']}")
            print(f"🔤 Language: {result['language']}")
            print(f"📏 Code Length: {result['code_length']} characters")
            
            # Display complexity metrics if available
            if 'complexity' in result:
                complexity = result['complexity']
                print(f"\n📊 COMPLEXITY METRICS:")
                print(f"   • Average Complexity: {complexity['average_complexity']}")
                print(f"   • Complexity Grade: {complexity['complexity_grade']}")
                print(f"   • Maintainability Index: {complexity['maintainability_index']}")
                print(f"   • Total Functions: {complexity['total_functions']}")
            
            print(f"\n🔒 SECURITY ANALYSIS:")
            print(f"   • SQL Injection Vulnerabilities: {result['sql_injection_count']}")
            print(f"   • XSS Vulnerabilities: {result['xss_count']}")
            print(f"   • Total Issues: {result['total_vulnerabilities']}")
            
            if result['vulnerabilities']:
                print(f"\n⚠️ VULNERABILITIES FOUND:\n")
                for vuln in result['vulnerabilities']:
                    print(f"   Line {vuln['line']}: {vuln['type']} [{vuln['severity']}]")
                    print(f"   Code: {vuln['code']}")
                    print(f"   Description: {vuln['description']}\n")
            
            if result['ai_analysis']:
                print(f"🤖 AI DETAILED ANALYSIS:\n")
                print(result['ai_analysis'])
            
            print("\n" + "="*70)
            
            # Build detailed voice output
            speech_parts = []
            
            # Complexity information
            if 'complexity' in result:
                complexity = result['complexity']
                speech_parts.append(f"Code complexity grade: {complexity['complexity_grade']}.")
            
            # Security information
            if result['total_vulnerabilities'] > 0:
                vuln_details = []
                if result['sql_injection_count'] > 0:
                    vuln_details.append(f"{result['sql_injection_count']} SQL injection")
                if result['xss_count'] > 0:
                    vuln_details.append(f"{result['xss_count']} XSS")
                
                vuln_summary = " and ".join(vuln_details) if len(vuln_details) > 1 else vuln_details[0]
                speech_parts.append(f"Found {result['total_vulnerabilities']} security issues: {vuln_summary}.")
                
                # List specific vulnerabilities
                for vuln in result['vulnerabilities'][:3]:  # Max 3 to avoid long speech
                    speech_parts.append(f"{vuln['type']} on line {vuln['line']}.")
                
                if len(result['vulnerabilities']) > 3:
                    speech_parts.append(f"And {len(result['vulnerabilities']) - 3} more issues.")
                
                speech_parts.append("Check the terminal for detailed analysis.")
            else:
                speech_parts.append("No security vulnerabilities found. Your code looks good!")
            
            speech = " ".join(speech_parts)
            self.voice_output.speak(speech)
            
            logger.info("Code analysis completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing code file: {e}")
            self.voice_output.speak("An error occurred while analyzing the code file.")
            return False
    
    def analyze_code_clipboard(self):
        """
        Analyze code from clipboard
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Analyzing code from clipboard...")
            
            # Analyze clipboard
            result = self.code_analyzer.analyze_clipboard()
            
            if result.get('error'):
                logger.error(f"Code analysis error: {result['error']}")
                self.voice_output.speak(result['error'])
                return False
            
            # Display results
            print("\n" + "="*70)
            print("💻 CODE ANALYSIS (FROM CLIPBOARD)")
            print("="*70)
            print(f"\n📏 Code Length: {result['code_length']} characters")
            print(f"\n🔒 Security Issues Found: {result['total_vulnerabilities']}")
            
            if result['vulnerabilities']:
                print(f"\n⚠️ VULNERABILITIES:\n")
                for vuln in result['vulnerabilities']:
                    print(f"   Line {vuln['line']}: {vuln['type']} [{vuln['severity']}]")
                    print(f"   Code: {vuln['code']}")
                    print(f"   Description: {vuln['description']}\n")
            
            if result['ai_analysis']:
                print(f"🤖 AI ANALYSIS:\n")
                print(result['ai_analysis'])
            
            print("\n" + "="*70)
            
            # Speak summary
            if result['total_vulnerabilities'] > 0:
                speech = f"Found {result['total_vulnerabilities']} security issues in the code."
            else:
                speech = "No security vulnerabilities found in the code."
            
            self.voice_output.speak(speech)
            
            logger.info("Clipboard code analysis completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing clipboard: {e}")
            self.voice_output.speak("An error occurred while analyzing the clipboard.")
            return False
    
    def _extract_first_sentences(self, text, max_sentences=3):
        """
        Extract first N sentences from text
        
        Args:
            text: Input text
            max_sentences: Maximum number of sentences
        
        Returns:
            str: First N sentences
        """
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return '. '.join(sentences[:max_sentences]) + '.'