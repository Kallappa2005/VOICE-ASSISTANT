"""
Browser Controller
Handles browser operations like opening, closing, and managing browser instances
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from src.core.logger import setup_logger
import os

logger = setup_logger(__name__)

class BrowserController:
    """Manages browser operations"""
    
    def __init__(self):
        """Initialize browser controller"""
        self.driver = None
        self.is_browser_open = False
        logger.info("Browser Controller initialized")
    
    def open_chrome(self, headless=False, start_url="https://www.google.com"):
        """
        Open Chrome browser
        
        Args:
            headless (bool): Run browser in headless mode (no GUI)
            start_url (str): URL to open on start (default: https://www.google.com)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.is_browser_open:
                logger.warning("Browser is already open")
                return False
            
            logger.info("Opening Chrome browser...")
            
            # Configure Chrome options
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument('--headless')
            
            # Additional options for stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            
            # Suppress logs
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set service with proper error handling
            try:
                # Try to install/get chromedriver
                driver_path = ChromeDriverManager().install()
                logger.info(f"ChromeDriver path: {driver_path}")
                
                # Verify the driver file exists and is executable
                if not os.path.exists(driver_path):
                    raise Exception(f"ChromeDriver not found at: {driver_path}")
                
                service = Service(driver_path)
                
            except Exception as driver_error:
                logger.error(f"ChromeDriver setup error: {driver_error}")
                
                # Fallback: Try system PATH chromedriver
                logger.info("Trying to use system chromedriver...")
                service = Service()
            
            # Initialize driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to blank page or specified URL
            if start_url:
                self.driver.get(start_url)
                logger.info(f"Opened with start URL: {start_url}")
            
            self.is_browser_open = True
            logger.info("Chrome browser opened successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open Chrome browser: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return False
    
    def close_browser(self):
        """
        Close the browser completely
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.is_browser_open or self.driver is None:
                logger.warning("No browser to close")
                return False
            
            logger.info("Closing browser...")
            self.driver.quit()
            self.driver = None
            self.is_browser_open = False
            logger.info("Browser closed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")
            return False
    
    def get_driver(self):
        """
        Get the current driver instance
        
        Returns:
            webdriver: Current driver or None
        """
        return self.driver
    
    def is_open(self):
        """
        Check if browser is open
        
        Returns:
            bool: True if browser is open
        """
        return self.is_browser_open
    
    def get_current_url(self):
        """
        Get current URL
        
        Returns:
            str: Current URL or None
        """
        try:
            if self.driver:
                return self.driver.current_url
            return None
        except Exception as e:
            logger.error(f"Error getting current URL: {e}")
            return None
    
    def get_page_title(self):
        """
        Get current page title
        
        Returns:
            str: Page title or None
        """
        try:
            if self.driver:
                return self.driver.title
            return None
        except Exception as e:
            logger.error(f"Error getting page title: {e}")
            return None


# """
# Browser Controller
# Handles browser operations like opening, closing, and managing browser instances
# """

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from src.core.logger import setup_logger
# import os

# logger = setup_logger(__name__)

# class BrowserController:
#     """Manages browser operations"""
    
#     def __init__(self):
#         """Initialize browser controller"""
#         self.driver = None
#         self.is_browser_open = False
#         logger.info("Browser Controller initialized")
    
#     def open_chrome(self, headless=False):
#         """
#         Open Chrome browser
        
#         Args:
#             headless (bool): Run browser in headless mode (no GUI)
        
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             if self.is_browser_open:
#                 logger.warning("Browser is already open")
#                 return False
            
#             logger.info("Opening Chrome browser...")
            
#             # Configure Chrome options
#             chrome_options = Options()
            
#             if headless:
#                 chrome_options.add_argument('--headless')
            
#             # Additional options for stability
#             chrome_options.add_argument('--no-sandbox')
#             chrome_options.add_argument('--disable-dev-shm-usage')
#             chrome_options.add_argument('--start-maximized')
#             chrome_options.add_argument('--disable-blink-features=AutomationControlled')
#             chrome_options.add_argument('--disable-gpu')
#             chrome_options.add_argument('--disable-extensions')
            
#             # Suppress logs
#             chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#             chrome_options.add_experimental_option('useAutomationExtension', False)
            
#             # Set service with proper error handling
#             try:
#                 # Try to install/get chromedriver
#                 driver_path = ChromeDriverManager().install()
#                 logger.info(f"ChromeDriver path: {driver_path}")
                
#                 # Verify the driver file exists and is executable
#                 if not os.path.exists(driver_path):
#                     raise Exception(f"ChromeDriver not found at: {driver_path}")
                
#                 service = Service(driver_path)
                
#             except Exception as driver_error:
#                 logger.error(f"ChromeDriver setup error: {driver_error}")
                
#                 # Fallback: Try system PATH chromedriver
#                 logger.info("Trying to use system chromedriver...")
#                 service = Service()
            
#             # Initialize driver
#             self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
#             self.is_browser_open = True
#             logger.info("Chrome browser opened successfully")
            
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to open Chrome browser: {e}")
#             logger.error(f"Error type: {type(e).__name__}")
#             return False
    
#     def close_browser(self):
#         """
#         Close the browser completely
        
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             if not self.is_browser_open or self.driver is None:
#                 logger.warning("No browser to close")
#                 return False
            
#             logger.info("Closing browser...")
#             self.driver.quit()
#             self.driver = None
#             self.is_browser_open = False
#             logger.info("Browser closed successfully")
            
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to close browser: {e}")
#             return False
    
#     def get_driver(self):
#         """
#         Get the current driver instance
        
#         Returns:
#             webdriver: Current driver or None
#         """
#         return self.driver
    
#     def is_open(self):
#         """
#         Check if browser is open
        
#         Returns:
#             bool: True if browser is open
#         """
#         return self.is_browser_open
    
#     def get_current_url(self):
#         """
#         Get current URL
        
#         Returns:
#             str: Current URL or None
#         """
#         try:
#             if self.driver:
#                 return self.driver.current_url
#             return None
#         except Exception as e:
#             logger.error(f"Error getting current URL: {e}")
#             return None
    
#     def get_page_title(self):
#         """
#         Get current page title
        
#         Returns:
#             str: Page title or None
#         """
#         try:
#             if self.driver:
#                 return self.driver.title
#             return None
#         except Exception as e:
#             logger.error(f"Error getting page title: {e}")
#             return None