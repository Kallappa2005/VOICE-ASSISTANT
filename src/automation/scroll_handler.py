"""
Scroll Handler
Handles scrolling operations on web pages
"""

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.core.logger import setup_logger
import time

logger = setup_logger(__name__)

class ScrollHandler:
    """Handles page scrolling operations"""
    
    def __init__(self, browser_controller):
        """
        Initialize scroll handler
        
        Args:
            browser_controller: BrowserController instance
        """
        self.browser = browser_controller
        logger.info("Scroll handler initialized")
    
    def scroll_down(self, amount='medium'):
        """
        Scroll down on page
        
        Args:
            amount (str): 'small', 'medium', 'large', or pixel value
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            # Determine scroll pixels
            scroll_pixels = self._get_scroll_pixels(amount)
            
            logger.info(f"Scrolling down by {scroll_pixels} pixels")
            
            # Execute scroll using JavaScript
            driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            
            time.sleep(0.5)  # Small delay for smooth effect
            logger.info("Scrolled down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll down: {e}")
            return False
    
    def scroll_up(self, amount='medium'):
        """
        Scroll up on page
        
        Args:
            amount (str): 'small', 'medium', 'large', or pixel value
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            # Determine scroll pixels (negative for up)
            scroll_pixels = -self._get_scroll_pixels(amount)
            
            logger.info(f"Scrolling up by {abs(scroll_pixels)} pixels")
            
            # Execute scroll using JavaScript
            driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
            
            time.sleep(0.5)
            logger.info("Scrolled up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll up: {e}")
            return False
    
    def scroll_to_top(self):
        """
        Scroll to top of page
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Scrolling to top of page")
            driver.execute_script("window.scrollTo(0, 0);")
            
            time.sleep(0.5)
            logger.info("Scrolled to top successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll to top: {e}")
            return False
    
    def scroll_to_bottom(self):
        """
        Scroll to bottom of page
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Scrolling to bottom of page")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(0.5)
            logger.info("Scrolled to bottom successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll to bottom: {e}")
            return False
    
    def scroll_to_element(self, element):
        """
        Scroll to a specific element
        
        Args:
            element: Selenium WebElement
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Scrolling to element")
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            time.sleep(0.5)
            logger.info("Scrolled to element successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scroll to element: {e}")
            return False
    
    def page_down(self):
        """
        Scroll down one page using Page Down key
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Pressing Page Down key")
            
            # Send Page Down key to body element
            actions = ActionChains(driver)
            actions.send_keys(Keys.PAGE_DOWN).perform()
            
            time.sleep(0.5)
            logger.info("Page Down executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute Page Down: {e}")
            return False
    
    def page_up(self):
        """
        Scroll up one page using Page Up key
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Pressing Page Up key")
            
            # Send Page Up key to body element
            actions = ActionChains(driver)
            actions.send_keys(Keys.PAGE_UP).perform()
            
            time.sleep(0.5)
            logger.info("Page Up executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute Page Up: {e}")
            return False
    
    def _get_scroll_pixels(self, amount):
        """
        Convert scroll amount to pixels
        
        Args:
            amount (str): 'small', 'medium', 'large', or number
        
        Returns:
            int: Pixel value
        """
        scroll_map = {
            'small': 200,
            'little': 200,
            'medium': 400,
            'normal': 400,
            'large': 600,
            'lot': 600,
            'more': 600
        }
        
        if isinstance(amount, int):
            return amount
        
        return scroll_map.get(amount.lower(), 400)  # Default: medium
    
    def get_scroll_position(self):
        """
        Get current scroll position
        
        Returns:
            dict: {'x': int, 'y': int} or None
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return None
            
            x = driver.execute_script("return window.pageXOffset;")
            y = driver.execute_script("return window.pageYOffset;")
            
            return {'x': x, 'y': y}
            
        except Exception as e:
            logger.error(f"Failed to get scroll position: {e}")
            return None