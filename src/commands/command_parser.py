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
        self.navigation_keywords = [
            'open', 'go to', 'navigate to', 'visit', 'show me', 'take me to'
        ]
        self.search_keywords = [
            'search for', 'search', 'find', 'look for', 'google'
        ]
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
        # SCREENSHOT KEYWORDS
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
        
        # YOUTUBE KEYWORDS - NEW
        self.youtube_search_keywords = [
            'search on youtube', 'youtube search', 'search youtube',
            'find on youtube', 'youtube find'
        ]
        self.open_youtube_keywords = [
            'open youtube', 'go to youtube', 'youtube'
        ]

        # NEW: Play video by number
        self.play_video_keywords = [
            'play video', 'play the video', 'open video', 'play that video'
        ]
        # Pause video - MORE SPECIFIC
        self.pause_video_keywords = [
            'pause video', 'pause the video', 'pause this video', 'pause'
        ]
        # Resume video - MORE SPECIFIC
        self.resume_video_keywords = [
            'resume video', 'resume the video', 'continue video', 
            'resume', 'unpause', 'unpause video'
        ]
        # Stop video - NEW
        self.stop_video_keywords = [
            'stop video', 'stop the video', 'stop playback'
        ]
        
        logger.info("Command parser initialized")
    
    def parse(self, command , context=None):
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
        
        # ====== YOUTUBE COMMANDS - CHECK FIRST ======
        
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
            
        # ====== VIDEO PLAYBACK CONTROL (Context-Aware) ======
            
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
                
        # Check for play video with number
        # for keyword in self.play_video_keywords:
        #     if keyword in command:
        #         # Extract number from command
        #         import re
                
        #         # Word to number mapping
        #         word_to_num = {
        #             'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
        #             'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
        #             'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        #             'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        #         }
                
        #         video_num = None
                
        #         # Check for number words
        #         for word, num in word_to_num.items():
        #             if word in command:
        #                 video_num = num
        #                 break
                
        #         # Check for digits
        #         if not video_num:
        #             numbers = re.findall(r'\d+', command)
        #             if numbers:
        #                 video_num = int(numbers[0])
                
        #         # Default to 1 if no number specified
        #         if not video_num:
        #             video_num = 1
                
        #         logger.info(f"Play video intent detected: video #{video_num}")
        #         return {
        #             'intent': 'play_video',
        #             'params': {'video_number': video_num}
        #         }
        
        # Check for pause video
        for keyword in self.pause_video_keywords:
            if keyword in command:
                logger.info("Pause video intent detected")
                return {'intent': 'pause_video', 'params': None}
        
        # Check for resume/play video (when on video page)
        for keyword in self.resume_video_keywords:
            if keyword in command:
                logger.info("Resume video intent detected")
                return {'intent': 'resume_video', 'params': None}
        
        
        
        # ====== SCREENSHOT COMMANDS ======
        
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
        
        # ====== OTHER COMMANDS ======
        
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
        
        # Default: treat as website name
        logger.info(f"Default navigation: {command}")
        return {
            'intent': 'navigate',
            'params': {'site': command}
        }