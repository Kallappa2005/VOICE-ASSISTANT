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
        self.screenshot_keywords = [
            'take screenshot', 'capture screen', 'save screenshot', 
            'screenshot', 'take picture', 'capture page', 'snap'
        ]
        self.fullpage_screenshot_keywords = [
            'full page screenshot', 'full screenshot', 'entire page screenshot'
        ]
        logger.info("Command parser initialized")
    
    def parse(self, command):
        """
        Parse voice command
        
        Args:
            command (str): Voice command text
        
        Returns:
            dict: Parsed command with intent and parameters
        """
        if not command:
            return {'intent': 'unknown', 'params': None}
        
        command = command.lower().strip()
        logger.info(f"Parsing command: {command}")
        
        # Check for full page screenshot
        for keyword in self.fullpage_screenshot_keywords:
            if keyword in command:
                logger.info("Full page screenshot intent detected")
                return {'intent': 'fullpage_screenshot', 'params': None}
        
        # Check for screenshot
        for keyword in self.screenshot_keywords:
            if keyword in command:
                logger.info("Screenshot intent detected")
                return {'intent': 'screenshot', 'params': None}
        
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