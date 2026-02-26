"""
Screenshot Handler
Captures and saves screenshots of web pages
"""

import os
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from src.core.logger import setup_logger

logger = setup_logger(__name__)

class ScreenshotHandler:
    """Handles screenshot capture and saving"""
    
    def __init__(self, browser_controller, screenshots_dir="data/screenshots"):
        """
        Initialize screenshot handler
        
        Args:
            browser_controller: BrowserController instance
            screenshots_dir (str): Directory to save screenshots
        """
        self.browser = browser_controller
        self.screenshots_dir = screenshots_dir
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        logger.info(f"Screenshot handler initialized (Save path: {self.screenshots_dir})")
    
    def take_screenshot(self, filename=None):
        """
        Take screenshot of current page
        
        Args:
            filename (str): Optional custom filename (without extension)
        
        Returns:
            tuple: (success, filepath)
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False, None
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"screenshot_{timestamp}"
            
            # Ensure filename ends with .png
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Full file path
            filepath = os.path.join(self.screenshots_dir, filename)
            
            logger.info(f"Taking screenshot: {filepath}")
            
            # Capture screenshot
            driver.save_screenshot(filepath)
            
            # Verify file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Screenshot saved successfully: {filepath} ({file_size} bytes)")
                return True, filepath
            else:
                logger.error("Screenshot file was not created")
                return False, None
            
        except WebDriverException as e:
            logger.error(f"WebDriver error taking screenshot: {e}")
            return False, None
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False, None
    
    def take_full_page_screenshot(self, filename=None):
        """
        Take full page screenshot (including scrollable area)
        
        Args:
            filename (str): Optional custom filename
        
        Returns:
            tuple: (success, filepath)
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False, None
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"fullpage_{timestamp}"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join(self.screenshots_dir, filename)
            
            logger.info(f"Taking full page screenshot: {filepath}")
            
            # Get page dimensions
            original_size = driver.get_window_size()
            
            # Get scroll height
            page_height = driver.execute_script("return document.body.scrollHeight")
            page_width = driver.execute_script("return document.body.scrollWidth")
            
            # Set window size to full page
            driver.set_window_size(page_width, page_height)
            
            # Take screenshot
            driver.save_screenshot(filepath)
            
            # Restore original window size
            driver.set_window_size(original_size['width'], original_size['height'])
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Full page screenshot saved: {filepath} ({file_size} bytes)")
                return True, filepath
            else:
                logger.error("Full page screenshot file was not created")
                return False, None
            
        except Exception as e:
            logger.error(f"Failed to take full page screenshot: {e}")
            # Try to restore window size
            try:
                if driver and original_size:
                    driver.set_window_size(original_size['width'], original_size['height'])
            except:
                pass
            return False, None
    
    def take_element_screenshot(self, element, filename=None):
        """
        Take screenshot of specific element
        
        Args:
            element: Selenium WebElement
            filename (str): Optional custom filename
        
        Returns:
            tuple: (success, filepath)
        """
        try:
            if not element:
                logger.error("No element provided")
                return False, None
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"element_{timestamp}"
            
            if not filename.endswith('.png'):
                filename += '.png'
            
            filepath = os.path.join(self.screenshots_dir, filename)
            
            logger.info(f"Taking element screenshot: {filepath}")
            
            # Capture element screenshot
            element.screenshot(filepath)
            
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Element screenshot saved: {filepath} ({file_size} bytes)")
                return True, filepath
            else:
                logger.error("Element screenshot file was not created")
                return False, None
            
        except Exception as e:
            logger.error(f"Failed to take element screenshot: {e}")
            return False, None
    
    def get_screenshot_count(self):
        """
        Get number of screenshots saved
        
        Returns:
            int: Number of screenshot files
        """
        try:
            if not os.path.exists(self.screenshots_dir):
                return 0
            
            files = [f for f in os.listdir(self.screenshots_dir) if f.endswith('.png')]
            count = len(files)
            logger.info(f"Screenshot count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count screenshots: {e}")
            return 0
    
    def list_screenshots(self):
        """
        Get list of all screenshot files
        
        Returns:
            list: List of screenshot filenames
        """
        try:
            if not os.path.exists(self.screenshots_dir):
                return []
            
            files = [f for f in os.listdir(self.screenshots_dir) if f.endswith('.png')]
            files.sort(reverse=True)  # Most recent first
            
            logger.info(f"Found {len(files)} screenshots")
            return files
            
        except Exception as e:
            logger.error(f"Failed to list screenshots: {e}")
            return []
    
    def delete_screenshot(self, filename):
        """
        Delete specific screenshot
        
        Args:
            filename (str): Screenshot filename
        
        Returns:
            bool: True if successful
        """
        try:
            filepath = os.path.join(self.screenshots_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted screenshot: {filename}")
                return True
            else:
                logger.warning(f"Screenshot not found: {filename}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to delete screenshot: {e}")
            return False
    
    def clear_all_screenshots(self):
        """
        Delete all screenshots
        
        Returns:
            int: Number of files deleted
        """
        try:
            files = self.list_screenshots()
            deleted = 0
            
            for filename in files:
                if self.delete_screenshot(filename):
                    deleted += 1
            
            logger.info(f"Deleted {deleted} screenshots")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to clear screenshots: {e}")
            return 0