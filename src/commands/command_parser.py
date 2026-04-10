"""
Command Parser
Parses voice commands and identifies intent
"""

from src.core.logger import setup_logger

logger = setup_logger(__name__)

class CommandParser:
    """Parse and interpret voice commands"""
    
    def __init__(self):
        """Initialize command parser"""
        # Navigation keywords
        self.navigation_keywords = [
            'open', 'go to', 'navigate to', 'visit', 'show me', 'take me to'
        ]
        self.search_keywords = [
            'search for', 'search', 'find', 'look for', 'google'
        ]
        
        # Scrolling keywords
        self.scroll_down_keywords = [
            'scroll down', 'page down', 'go down', 'move down'
        ]
        self.scroll_up_keywords = [
            'scroll up', 'page up', 'go up', 'move up'
        ]
        self.scroll_top_keywords = [
            'scroll to top', 'go to top', 'top of page', 'scroll top'
        ]
        self.scroll_bottom_keywords = [
            'scroll to bottom', 'go to bottom', 'bottom of page', 'scroll bottom'
        ]
        
        
        # Tab management keywords
        self.close_tab_keywords = [
            'close tab', 'close this tab', 'close current tab'
        ]
        self.close_browser_keywords = [
            'close browser', 'close all tabs', 'exit browser', 'quit browser'
        ]
        self.switch_tab_keywords = [
            'switch tab', 'next tab', 'change tab'
        ]
        self.previous_tab_keywords = [
            'previous tab', 'last tab', 'go back tab'
        ]
        self.new_tab_keywords = [
            'new tab', 'open new tab', 'create tab'
        ]
        
        # Screenshot keywords
        self.fullpage_screenshot_keywords = [
            'full page screenshot', 'full screenshot', 'entire page screenshot'
        ]
        self.delete_all_screenshots_keywords = [
            'delete all screenshots', 'clear screenshots', 'remove all screenshots',
            'clear all screenshots'
        ]
        self.delete_screenshot_keywords = [
            'delete screenshot', 'remove screenshot', 'delete last screenshot', 
            'delete picture'
        ]
        self.list_screenshots_keywords = [
            'list screenshots', 'show screenshots', 'display screenshots',
            'how many screenshots'
        ]
        self.screenshot_keywords = [
            'take screenshot', 'capture screen', 'save screenshot', 
            'take picture', 'capture page', 'snap'
        ]
        
        # YouTube keywords
        self.youtube_search_keywords = [
            'search on youtube', 'youtube search', 'search youtube',
            'find on youtube', 'youtube find'
        ]
        self.open_youtube_keywords = [
            'open youtube', 'go to youtube', 'youtube'
        ]
        
        # Video playback keywords
        self.play_video_keywords = [
            'play video', 'play the video', 'open video', 'play that video'
        ]
        self.pause_video_keywords = [
            'pause video', 'pause the video', 'pause this video', 'pause'
        ]
        self.resume_video_keywords = [
            'resume video', 'resume the video', 'continue video', 
            'resume', 'unpause', 'unpause video'
        ]
        self.stop_video_keywords = [
            'stop video', 'stop the video', 'stop playback'
        ]
        
        # Ad-skip keywords — checked FIRST among video controls
        self.skip_ad_keywords = [
            'skip ad', 'skip the ad', 'skip advertisement',
            'skip this ad', 'skip ads', 'bypass ad',
            'close ad', 'dismiss ad',
        ]
        
        # ==================== AI KEYWORDS (UPDATED - BOTH SPELLINGS) ====================
        
        # Wake/Sleep keywords
        self.wake_keywords = [
            'hey assistant', 'wake up', 'hello assistant', 'hey there'
        ]
        self.sleep_keywords = [
            'sleep', 'go to sleep', 'sleep mode'
        ]
        self.exit_keywords = [
            'exit', 'quit', 'goodbye', 'bye', 'close assistant'
        ]
        
        # Webpage analysis keywords (BOTH AMERICAN & BRITISH SPELLING)
        self.analyze_page_keywords = [
            # American spelling
            'analyze this page', 'analyze current page', 'analyze page',
            'analyze the page', 'check this page', 'review this page',
            # British spelling
            'analyse this page', 'analyse current page', 'analyse page',
            'analyse the page',
        ]
        self.summarize_page_keywords = [
            # American spelling
            'summarize this page', 'summarize page', 'page summary',
            'summarize the page', 'give me summary', 'what is this page about',
            # British spelling
            'summarise this page', 'summarise page', 'summarise the page',
        ]
        self.key_points_keywords = [
            'key points', 'main points', 'give me key points',
            'what are the key points', 'extract key points', 'important points',
            'show key points', 'tell me key points',
        ]
        
        # Code analysis keywords (BOTH AMERICAN & BRITISH SPELLING)
        self.analyze_code_file_keywords = [
            # American spelling
            'analyze code file', 'check code file', 'review code file',
            'analyze file', 'check file for security',
            'analyze code from file', 'check code from file',  # Added variations
            # British spelling
            'analyse code file', 'analyse file',
            'analyse code from file', 'check code from file',  # Added variations
        ]
        self.analyze_code_clipboard_keywords = [
            # American spelling
            'analyze clipboard', 'check clipboard', 'analyze code clipboard',
            'check code', 'analyze code', 'review code',
            # British spelling
            'analyse clipboard', 'analyse code clipboard', 'analyse code',
        ]
        
        # ==================== CODING MODE KEYWORDS ====================
        
        # Triggered when user says "start coding", "coding mode", etc.
        # These are checked after AI commands but before YouTube/navigation.
        self.start_coding_keywords = [
            'start coding',
            'coding mode',
            'start coding mode',
            'begin coding',
            'launch project',
            'open project',
            'dev mode',
            'development mode',
        ]

        # ==================== STUDY MODE KEYWORDS ====================

        # Triggered when user says "study mode", "start studying", etc.
        # Checked after coding mode, before YouTube/navigation.
        # Topic is extracted from the remainder of the command when present.
        self.study_mode_keywords = [
            'study mode',
            'start studying',
            'start study mode',
            'begin studying',
            'focus mode',
            'learning mode',
            'study session',
            'start study session',
        ]

        # ==================== PROJECT SETUP KEYWORDS ====================

        # React starter project setup
        self.react_project_setup_keywords = [
            'set up react project',
            'setup react project',
            'create react project',
            'build react project',
            'make react project',
            'set up react app',
            'setup react app',
            'create react app',
            'build react app',
        ]

        # Flask starter project setup
        self.flask_project_setup_keywords = [
            'set up flask project',
            'setup flask project',
            'create flask project',
            'build flask project',
            'make flask project',
            'set up flask app',
            'setup flask app',
            'create flask app',
            'build flask app',
        ]

        # Common STT mishears for "flask" in setup commands.
        # Example: "set up last project" should still map to Flask setup.
        self.flask_project_setup_misheard_keywords = [
            'set up last project',
            'setup last project',
            'create last project',
            'build last project',
            'make last project',
            'open last project',
            'set up class project',
            'setup class project',
            'create class project',
            'build class project',
            'make class project',
            'open class project',
            'set up flusk project',
            'setup flusk project',
            'create flusk project',
            'build flusk project',
            'make flusk project',
            'open flusk project',
            'open flask project',
            'set up last app',
            'setup last app',
            'open last app',
            'set up class app',
            'setup class app',
            'open class app',
            'set up flusk app',
            'setup flusk app',
            'open flusk app',
            'open flask app',
        ]

    
    def parse(self, command, context=None):
        """
        Parse voice command
        
        Args:
            command (str): Voice command text
            context (dict): Optional context (e.g., {'on_video_page': True})
        
        Returns:
            dict: Parsed command with intent and parameters
        """
        if not command:
            return {'intent': 'unknown', 'params': None}
        
        command = command.lower().strip()
        logger.info(f"Parsing command: {command}")

        if context:
            logger.info(f"Context: {context}")
        
        # ==================== AI COMMANDS (CHECK FIRST - HIGHEST PRIORITY) ====================
        
        # Wake command
        for keyword in self.wake_keywords:
            if keyword in command:
                logger.info("Wake intent detected")
                return {'intent': 'wake', 'params': None}
        
        # Sleep command
        for keyword in self.sleep_keywords:
            if keyword in command:
                logger.info("Sleep intent detected")
                return {'intent': 'sleep', 'params': None}
        
        # Exit command
        for keyword in self.exit_keywords:
            if keyword in command:
                logger.info("Exit intent detected")
                return {'intent': 'exit', 'params': None}
        
        # Analyze current page (HIGH PRIORITY - BEFORE NAVIGATION)
        for keyword in self.analyze_page_keywords:
            if keyword in command:
                logger.info("Analyze page intent detected")
                return {'intent': 'analyze_current_page', 'params': None}
        
        # Summarize page (HIGH PRIORITY - BEFORE NAVIGATION)
        for keyword in self.summarize_page_keywords:
            if keyword in command:
                logger.info("Summarize page intent detected")
                return {'intent': 'summarize_page', 'params': None}
        
        # Get key points (HIGH PRIORITY - BEFORE NAVIGATION)
        for keyword in self.key_points_keywords:
            if keyword in command:
                logger.info("Get key points intent detected")
                return {'intent': 'get_key_points', 'params': None}
        
        # Analyze code file (HIGH PRIORITY - BEFORE NAVIGATION)
        for keyword in self.analyze_code_file_keywords:
            if keyword in command:
                # Extract file path
                # Example: "analyze code file test.py" or "analyze code file desktop/test.py"
                parts = command.split('file')
                if len(parts) > 1:
                    file_path = parts[1].strip()
                    logger.info(f"Analyze code file intent detected: {file_path}")
                    return {
                        'intent': 'analyze_code_file',
                        'params': {'file_path': file_path}
                    }
                else:
                    # No file path specified
                    logger.info("Analyze code file intent detected (no path)")
                    return {
                        'intent': 'analyze_code_file',
                        'params': {'file_path': ''}
                    }
        
        # Analyze clipboard (HIGH PRIORITY - BEFORE NAVIGATION)
        for keyword in self.analyze_code_clipboard_keywords:
            if keyword in command:
                logger.info("Analyze clipboard intent detected")
                return {'intent': 'analyze_code_clipboard', 'params': None}
        
        # ==================== CODING MODE ====================
        
        # Checked after AI commands, before YouTube/navigation
        for keyword in self.start_coding_keywords:
            if keyword in command:
                logger.info("Start coding intent detected")
                return {'intent': 'start_coding', 'params': None}
        
        # ==================== STUDY MODE ====================
        
        # Checked after coding mode, before YouTube/navigation
        # Topic is extracted from the remainder of the command when present.
        for keyword in self.study_mode_keywords:
            if keyword in command:
                # Extract topic after the keyword
                # Example: "study mode react" → topic = "react"
                # Example: "start studying javascript" → topic = "javascript"
                parts = command.split(keyword, 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                    logger.info(f"Start study intent detected (topic: '{topic}')")
                    return {
                        'intent': 'start_study',
                        'params': {'topic': topic}
                    }
                else:
                    logger.info("Start study intent detected (no topic)")
                    return {'intent': 'start_study', 'params': None}

        # ==================== PROJECT SETUP ====================

        # React project setup
        for keyword in self.react_project_setup_keywords:
            if keyword in command:
                remainder = command.split(keyword, 1)[1].strip()
                logger.info(f"React project setup intent detected: {remainder}")
                return {
                    'intent': 'setup_project',
                    'params': {
                        'project_type': 'react',
                        'project_name': remainder or None,
                    }
                }

        # Flask project setup
        for keyword in self.flask_project_setup_keywords:
            if keyword in command:
                remainder = command.split(keyword, 1)[1].strip()
                logger.info(f"Flask project setup intent detected: {remainder}")
                return {
                    'intent': 'setup_project',
                    'params': {
                        'project_type': 'flask',
                        'project_name': remainder or None,
                    }
                }

        # Flask project setup (speech-misheard variations)
        for keyword in self.flask_project_setup_misheard_keywords:
            if keyword in command:
                remainder = command.split(keyword, 1)[1].strip()
                logger.info(f"Flask project setup intent detected (misheard phrase): {remainder}")
                return {
                    'intent': 'setup_project',
                    'params': {
                        'project_type': 'flask',
                        'project_name': remainder or None,
                    }
                }

        # Extra tolerant fallback for phrases like:
        # "set up last project", "setup class app", "create flusk project"
        setup_verbs = ['set up', 'setup', 'create', 'build', 'make', 'open']
        flask_aliases = ['flask', 'flusk', 'last', 'class']
        setup_targets = ['project', 'app']
        if any(verb in command for verb in setup_verbs) and any(alias in command for alias in flask_aliases):
            if any(target in command for target in setup_targets):
                logger.info("Flask project setup intent detected (tolerant fallback)")
                return {
                    'intent': 'setup_project',
                    'params': {
                        'project_type': 'flask',
                        'project_name': None,
                    }
                }
        
        # ==================== YOUTUBE COMMANDS ====================
        
        # Check for YouTube search
        for keyword in self.youtube_search_keywords:
            if keyword in command:
                # Extract query after keyword
                query = command.split(keyword)[-1].strip()
                if query:
                    logger.info(f"YouTube search intent detected: {query}")
                    return {
                        'intent': 'youtube_search',
                        'params': {'query': query}
                    }
                
        # Check for open YouTube
        for keyword in self.open_youtube_keywords:
            if command == keyword or command.startswith(keyword + ' '):
                logger.info("Open YouTube intent detected")
                return {'intent': 'open_youtube', 'params': None}
        
        # ==================== VIDEO PLAYBACK CONTROL ====================
            
        # Check for SKIP AD first (must be before pause/stop so 'skip' is unambiguous)
        for keyword in self.skip_ad_keywords:
            if keyword in command:
                logger.info("Skip ad intent detected")
                return {'intent': 'skip_ad', 'params': None}

        # Check for STOP VIDEO first (most specific)
        for keyword in self.stop_video_keywords:
            if keyword in command:
                logger.info("Stop video intent detected")
                return {'intent': 'stop_video', 'params': None}
        
        # Check for PAUSE VIDEO
        for keyword in self.pause_video_keywords:
            if keyword in command:
                logger.info("Pause video intent detected")
                return {'intent': 'pause_video', 'params': None}
        
        # Check for RESUME VIDEO
        for keyword in self.resume_video_keywords:
            if keyword in command:
                logger.info("Resume video intent detected")
                return {'intent': 'resume_video', 'params': None}
        
        # Check for PLAY VIDEO (with number OR resume if on video page)
        for keyword in self.play_video_keywords:
            if keyword in command:
                import re
                
                # If on video page and no number mentioned → resume
                on_video_page = context and context.get('on_video_page', False)
                
                # Check if command has a number
                has_number = False
                word_to_num = {
                    'first': 1, '1st': 1, 'second': 2, '2nd': 2, 'third': 3, '3rd': 3,
                    'fourth': 4, '4th': 4, 'fifth': 5, '5th': 5, 'sixth': 6, '6th': 6,
                    'seventh': 7, '7th': 7, 'eighth': 8, '8th': 8, 'ninth': 9, '9th': 9,
                    'tenth': 10, '10th': 10, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
                    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
                }

                video_num = None
                
                # Check for number words
                for word, num in sorted(word_to_num.items(), key=lambda x: -len(x[0])):
                    if word in command:
                        video_num = num
                        has_number = True
                        break
                
                # Check for digits
                if not video_num:
                    numbers = re.findall(r'\d+', command)
                    if numbers:
                        video_num = int(numbers[0])
                        has_number = True
                
                # DECISION: Resume or Play new video?
                if on_video_page and not has_number:
                    # On video page, no number → RESUME
                    logger.info("Resume video intent detected (play on video page)")
                    return {'intent': 'resume_video', 'params': None}
                else:
                    # Has number OR not on video page → PLAY VIDEO
                    if not video_num:
                        video_num = 1  # Default
                    
                    logger.info(f"Play video intent detected: video #{video_num}")
                    return {
                        'intent': 'play_video',
                        'params': {'video_number': video_num}
                    }
        
        # ==================== SCREENSHOT COMMANDS ====================
        
        # Check for delete all screenshots FIRST
        for keyword in self.delete_all_screenshots_keywords:
            if keyword in command:
                logger.info("Delete all screenshots intent detected")
                return {'intent': 'delete_all_screenshots', 'params': None}
        
        # Check for list screenshots
        for keyword in self.list_screenshots_keywords:
            if keyword in command:
                logger.info("List screenshots intent detected")
                return {'intent': 'list_screenshots', 'params': None}
        
        # Check for delete screenshot (single)
        for keyword in self.delete_screenshot_keywords:
            if keyword in command:
                logger.info("Delete screenshot intent detected")
                return {'intent': 'delete_screenshot', 'params': None}
        
        # Check for full page screenshot
        for keyword in self.fullpage_screenshot_keywords:
            if keyword in command:
                logger.info("Full page screenshot intent detected")
                return {'intent': 'fullpage_screenshot', 'params': None}
        
        # Check for screenshot (GENERAL - LAST)
        for keyword in self.screenshot_keywords:
            if keyword in command:
                logger.info("Screenshot intent detected")
                return {'intent': 'screenshot', 'params': None}
        
        # ==================== TAB MANAGEMENT ====================
        
        # Check for close browser
        for keyword in self.close_browser_keywords:
            if keyword in command:
                logger.info("Close browser intent detected")
                return {'intent': 'close_browser', 'params': None}
        
        # Check for close tab
        for keyword in self.close_tab_keywords:
            if keyword in command:
                logger.info("Close tab intent detected")
                return {'intent': 'close_tab', 'params': None}
        
        # Check for new tab
        for keyword in self.new_tab_keywords:
            if keyword in command:
                logger.info("New tab intent detected")
                return {'intent': 'new_tab', 'params': None}
        
        # Check for previous tab
        for keyword in self.previous_tab_keywords:
            if keyword in command:
                logger.info("Previous tab intent detected")
                return {'intent': 'previous_tab', 'params': None}
        
        # Check for switch/next tab
        for keyword in self.switch_tab_keywords:
            if keyword in command:
                logger.info("Switch tab intent detected")
                return {'intent': 'switch_tab', 'params': None}
        
        # ==================== SCROLLING ====================
        
        # Check for scroll to top
        for keyword in self.scroll_top_keywords:
            if keyword in command:
                logger.info("Scroll to top intent detected")
                return {'intent': 'scroll_top', 'params': None}
        
        # Check for scroll to bottom
        for keyword in self.scroll_bottom_keywords:
            if keyword in command:
                logger.info("Scroll to bottom intent detected")
                return {'intent': 'scroll_bottom', 'params': None}
        
        # Check for scroll down
        for keyword in self.scroll_down_keywords:
            if keyword in command:
                amount = 'medium'
                if 'little' in command or 'small' in command:
                    amount = 'small'
                elif 'lot' in command or 'large' in command or 'more' in command:
                    amount = 'large'
                
                logger.info(f"Scroll down intent detected: {amount}")
                return {
                    'intent': 'scroll_down',
                    'params': {'amount': amount}
                }
        
        # Check for scroll up
        for keyword in self.scroll_up_keywords:
            if keyword in command:
                amount = 'medium'
                if 'little' in command or 'small' in command:
                    amount = 'small'
                elif 'lot' in command or 'large' in command or 'more' in command:
                    amount = 'large'
                
                logger.info(f"Scroll up intent detected: {amount}")
                return {
                    'intent': 'scroll_up',
                    'params': {'amount': amount}
                }
        
        # ==================== NAVIGATION & SEARCH (LOWEST PRIORITY) ====================
        
        # Check for navigation commands
        for keyword in self.navigation_keywords:
            if keyword in command:
                site = command.replace(keyword, '').strip()
                logger.info(f"Navigation intent detected: {site}")
                return {
                    'intent': 'navigate',
                    'params': {'site': site}
                }
        
        # Check for search commands
        for keyword in self.search_keywords:
            if command.startswith(keyword):
                query = command.replace(keyword, '').strip()
                logger.info(f"Search intent detected: {query}")
                return {
                    'intent': 'search',
                    'params': {'query': query}
                }
        
        # Default: treat as website name (LAST RESORT)
        logger.info(f"Default navigation: {command}")
        return {
            'intent': 'navigate',
            'params': {'site': command}
        }