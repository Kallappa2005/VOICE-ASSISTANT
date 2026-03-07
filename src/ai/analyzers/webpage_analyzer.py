"""
Webpage Analyzer
Analyzes webpage content using AI
"""

from bs4 import BeautifulSoup
import re
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class WebpageAnalyzer:
    """Analyze webpage content"""
    
    def __init__(self, gemini_client):
        """
        Initialize webpage analyzer
        
        Args:
            gemini_client: GeminiClient instance
        """
        self.gemini = gemini_client
        logger.info("WebPageAnalyzer initialized")
    
    def extract_content(self, driver):
        """
        Extract meaningful content from webpage
        
        Args:
            driver: Selenium WebDriver instance
        
        Returns:
            dict: {
                'title': Page title,
                'url': Current URL,
                'main_content': Extracted text content,
                'content_length': Character count
            }
        """
        try:
            # Get page info
            title = driver.title
            url = driver.current_url
            
            logger.info(f"Extracting content from: {title}")
            
            # Get page source
            page_source = driver.page_source
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # ==================== IMPROVED CONTENT EXTRACTION ====================
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Try to find main content area (prioritize these tags)
            main_content = None
            
            # Strategy 1: Look for main content containers
            content_selectors = [
                'main',
                'article',
                '[role="main"]',
                '#content',
                '#main-content',
                '.content',
                '.main-content',
                '.article-content',
                '#mw-content-text',  # Wikipedia specific
                '.mw-parser-output',  # Wikipedia specific
            ]
            
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    logger.info(f"Found main content using selector: {selector}")
                    break
            
            # Strategy 2: If no main container found, get all paragraphs and headings
            if not main_content:
                logger.info("No main content container found, extracting all text")
                main_content = soup.body if soup.body else soup
            
            # Extract text content
            if main_content:
                # Get all text elements
                text_elements = []
                
                # Extract headings (h1-h6)
                for heading in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    heading_text = heading.get_text(strip=True)
                    if heading_text and len(heading_text) > 1:
                        text_elements.append(f"\n## {heading_text}\n")
                
                # Extract paragraphs
                for para in main_content.find_all(['p', 'li', 'div']):
                    para_text = para.get_text(strip=True)
                    # Filter out very short text (likely noise)
                    if para_text and len(para_text) > 20:
                        text_elements.append(para_text)
                
                # Combine all text
                extracted_text = '\n'.join(text_elements)
                
            else:
                # Fallback: Get all text from body
                extracted_text = soup.get_text(separator='\n', strip=True)
            
            # ==================== CLEAN UP TEXT ====================
            
            # Remove excessive whitespace
            extracted_text = re.sub(r'\n\s*\n+', '\n\n', extracted_text)
            extracted_text = re.sub(r' +', ' ', extracted_text)
            
            # Remove lines that are too short (likely noise)
            lines = extracted_text.split('\n')
            cleaned_lines = [line for line in lines if len(line.strip()) > 15 or line.startswith('##')]
            extracted_text = '\n'.join(cleaned_lines)
            
            # Truncate if too long (keep first 15000 chars for AI processing)
            max_length = 15000
            if len(extracted_text) > max_length:
                logger.info(f"Content too long ({len(extracted_text)} chars), truncating to {max_length}")
                extracted_text = extracted_text[:max_length] + "\n...[Content truncated for processing]"
            
            content_length = len(extracted_text)
            
            logger.info(f"Content extracted: {content_length} characters")
            
            # Validate we have meaningful content
            if content_length < 100:
                logger.warning(f"Very little content extracted ({content_length} chars)")
            
            return {
                'title': title,
                'url': url,
                'main_content': extracted_text,
                'content_length': content_length
            }
            
        except Exception as e:
            logger.error(f"Error extracting webpage content: {e}")
            return {
                'title': 'Unknown',
                'url': 'Unknown',
                'main_content': '',
                'content_length': 0
            }
    
    def analyze_page(self, content_data):
        """
        Analyze webpage content using Gemini AI
        
        Args:
            content_data: Dict with title, url, main_content
        
        Returns:
            str: AI analysis of the webpage
        """
        try:
            title = content_data.get('title', 'Unknown')
            url = content_data.get('url', 'Unknown')
            content = content_data.get('main_content', '')
            
            if not content or len(content) < 50:
                return "Error: Could not extract meaningful content from the page."
            
            logger.info(f"Analyzing page: {title} ({len(content)} chars)")
            
            # Create prompt for Gemini
            prompt = f"""You are analyzing a webpage. Please provide a comprehensive analysis.

**Page Information:**
- Title: {title}
- URL: {url}

**Page Content:**
{content}

**Instructions:**
Please provide:
1. A detailed summary of the main topic (2-3 paragraphs)
2. Key themes and concepts discussed
3. Important facts or statistics mentioned
4. Main conclusions or takeaways

Format your response clearly with headings."""
            
            # Get AI response
            response = self.gemini.generate_text(prompt)
            
            if response:
                logger.info("Page analysis completed")
                return response
            else:
                return "Error: Could not generate analysis."
            
        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            return f"Error during analysis: {str(e)}"
    
    def summarize_page(self, content_data):
        """
        Generate a brief summary of the webpage
        
        Args:
            content_data: Dict with title, url, main_content
        
        Returns:
            str: Brief summary
        """
        try:
            title = content_data.get('title', 'Unknown')
            content = content_data.get('main_content', '')
            
            if not content or len(content) < 50:
                return "Error: Could not extract meaningful content from the page."
            
            logger.info(f"Summarizing page: {title}")
            
            # Create prompt for Gemini
            prompt = f"""Summarize this webpage in 2-3 sentences:

**Page Title:** {title}

**Content:**
{content}

**Instructions:**
Provide a concise, clear summary focusing on the main topic and key points. Keep it brief and informative."""
            
            # Get AI response
            response = self.gemini.generate_text(prompt)
            
            if response:
                logger.info("Page summary completed")
                return response
            else:
                return "Error: Could not generate summary."
            
        except Exception as e:
            logger.error(f"Error summarizing page: {e}")
            return f"Error during summarization: {str(e)}"
    
    def extract_key_points(self, content_data):
        """
        Extract key points from webpage
        
        Args:
            content_data: Dict with title, url, main_content
        
        Returns:
            list: List of key points (strings)
        """
        try:
            title = content_data.get('title', 'Unknown')
            content = content_data.get('main_content', '')
            
            if not content or len(content) < 50:
                logger.error(f"Insufficient content for key points: {len(content)} chars")
                return ["Error: Could not extract meaningful content from the page."]
            
            logger.info(f"Extracting key points from: {title} ({len(content)} chars)")
            
            # Create prompt for Gemini
            prompt = f"""Extract the most important key points from this webpage content.

**Page Title:** {title}

**Content:**
{content}

**Instructions:**
Identify and list 5-10 key points from this content. Each point should be:
- A complete sentence
- Capture an important fact, concept, or insight
- Be clear and concise

Format: Return ONLY a numbered list (1., 2., 3., etc.) with each key point on a new line.
Do NOT include any introductory text or explanations, just the numbered list."""
            
            # Get AI response
            response = self.gemini.generate_text(prompt)
            
            if not response:
                logger.error("No response from Gemini")
                return ["Error: Could not generate key points."]
            
            # Parse response into list
            key_points = []
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                # Check if line starts with number (1., 2., etc.) or bullet (-, •, *)
                if re.match(r'^\d+[\.\)]\s+', line) or re.match(r'^[-•*]\s+', line):
                    # Remove number/bullet and clean
                    point = re.sub(r'^\d+[\.\)]\s+', '', line)
                    point = re.sub(r'^[-•*]\s+', '', point)
                    point = point.strip()
                    if point and len(point) > 10:  # Ensure meaningful content
                        key_points.append(point)
            
            # If parsing failed, try to split by newlines
            if not key_points:
                logger.warning("Could not parse numbered list, using line-by-line")
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 20:  # Filter out short lines
                        key_points.append(line)
            
            # Validate we have points
            if not key_points:
                logger.error("No key points extracted from response")
                return ["Error: Could not extract key points from the content."]
            
            logger.info(f"Extracted {len(key_points)} key points")
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return [f"Error during key point extraction: {str(e)}"]