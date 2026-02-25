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