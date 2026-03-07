"""
Browser Controller
Handles all browser operations
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from src.core.logger import setup_logger
import os

logger = setup_logger(__name__)

class BrowserController:
    """Control Chrome browser with Selenium"""
    
    def __init__(self):
        """Initialize browser controller"""
        self.driver = None
        self._is_open = False
        logger.info("Browser Controller initialized")
    
    def open_chrome(self):
        """
        Open Chrome browser
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Opening Chrome browser...")
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # ==================== FIX: Get correct ChromeDriver path ====================
            
            try:
                # Install/Get ChromeDriver
                driver_path = ChromeDriverManager().install()
                logger.info(f"ChromeDriver path from manager: {driver_path}")
                
                # FIX: Extract the directory and find chromedriver.exe
                driver_dir = os.path.dirname(driver_path)
                
                # Look for chromedriver.exe in the directory
                possible_paths = [
                    os.path.join(driver_dir, 'chromedriver.exe'),
                    os.path.join(driver_dir, 'chromedriver-win32', 'chromedriver.exe'),
                    driver_path,  # Try original path
                ]
                
                chromedriver_exe = None
                for path in possible_paths:
                    if os.path.exists(path) and path.endswith('.exe'):
                        chromedriver_exe = path
                        logger.info(f"Found ChromeDriver at: {chromedriver_exe}")
                        break
                
                if not chromedriver_exe:
                    # If not found, search the directory
                    for root, dirs, files in os.walk(driver_dir):
                        for file in files:
                            if file == 'chromedriver.exe':
                                chromedriver_exe = os.path.join(root, file)
                                logger.info(f"Found ChromeDriver via search: {chromedriver_exe}")
                                break
                        if chromedriver_exe:
                            break
                
                if not chromedriver_exe:
                    raise FileNotFoundError("Could not find chromedriver.exe")
                
                # Create service with correct path
                service = Service(chromedriver_exe)
                
            except Exception as e:
                logger.error(f"Error setting up ChromeDriver: {e}")
                raise
            
            # ==================== Initialize WebDriver ====================
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            self._is_open = True
            logger.info("✅ Chrome browser opened successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open Chrome browser: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            self._is_open = False
            return False
    
    def get_driver(self):
        """
        Get the Selenium WebDriver instance
        
        Returns:
            WebDriver: Selenium driver instance or None
        """
        return self.driver
    
    def is_open(self):
        """Check if browser is open"""
        return self._is_open and self.driver is not None
    
    def navigate_to(self, url):
        """
        Navigate to URL
        
        Args:
            url: URL to navigate to
        
        Returns:
            bool: Success status
        """
        if not self.is_open():
            logger.error("Browser is not open")
            return False
        
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            time.sleep(2)  # Wait for page load
            return True
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def get_current_url(self):
        """Get current URL"""
        if self.is_open():
            return self.driver.current_url
        return None
    
    def get_page_title(self):
        """Get current page title"""
        if self.is_open():
            return self.driver.title
        return None
    
    def close_browser(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
                self._is_open = False
                logger.info("✅ Browser closed")
                return True
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        
        return False
    
    def execute_script(self, script):
        """
        Execute JavaScript
        
        Args:
            script: JavaScript code
        
        Returns:
            Result of script execution
        """
        if not self.is_open():
            return None
        
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return None
    
    def scroll_down(self, amount='medium'):
        """
        Scroll down the page
        
        Args:
            amount: 'small', 'medium', or 'large'
        """
        if not self.is_open():
            return False
        
        scroll_pixels = {
            'small': 300,
            'medium': 600,
            'large': 1200
        }
        
        pixels = scroll_pixels.get(amount, 600)
        
        try:
            self.execute_script(f"window.scrollBy(0, {pixels});")
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def scroll_up(self, amount='medium'):
        """
        Scroll up the page
        
        Args:
            amount: 'small', 'medium', or 'large'
        """
        if not self.is_open():
            return False
        
        scroll_pixels = {
            'small': 300,
            'medium': 600,
            'large': 1200
        }
        
        pixels = scroll_pixels.get(amount, 600)
        
        try:
            self.execute_script(f"window.scrollBy(0, -{pixels});")
            return True
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return False
    
    def scroll_to_top(self):
        """Scroll to top of page"""
        if not self.is_open():
            return False
        
        try:
            self.execute_script("window.scrollTo(0, 0);")
            return True
        except Exception as e:
            logger.error(f"Scroll to top failed: {e}")
            return False
    
    def scroll_to_bottom(self):
        """Scroll to bottom of page"""
        if not self.is_open():
            return False
        
        try:
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            return True
        except Exception as e:
            logger.error(f"Scroll to bottom failed: {e}")
            return False
    
    def take_screenshot(self, filename):
        """
        Take a screenshot
        
        Args:
            filename: Path to save screenshot
        
        Returns:
            bool: Success status
        """
        if not self.is_open():
            logger.error("Browser is not open")
            return False
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def get_page_source(self):
        """Get page HTML source"""
        if self.is_open():
            return self.driver.page_source
        return None