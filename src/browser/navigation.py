"""
Navigation Module
Handles website navigation and URL management
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.core.logger import setup_logger
import time

logger = setup_logger(__name__)

class Navigation:
    """Handles browser navigation operations"""
    
    def __init__(self, browser_controller):
        """
        Initialize navigation handler
        
        Args:
            browser_controller: BrowserController instance
        """
        self.browser = browser_controller
        self.common_sites = {
            'youtube': 'https://www.youtube.com',
            'google': 'https://www.google.com',
            'gmail': 'https://mail.google.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'reddit': 'https://www.reddit.com',
            'twitter': 'https://www.twitter.com',
            'facebook': 'https://www.facebook.com',
            'instagram': 'https://www.instagram.com',
            'linkedin': 'https://www.linkedin.com',
            'amazon': 'https://www.amazon.in',
            'flipkart': 'https://www.flipkart.com',
        }
        logger.info("Navigation handler initialized")
    
    def goto_url(self, url, new_tab=False):
        """
        Navigate to specific URL
        
        Args:
            url (str): URL to navigate to
            new_tab (bool): Open in new tab if True
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            # Add https:// if not present
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'https://' + url
            
            logger.info(f"Navigating to: {url} (New tab: {new_tab})")
            
            if new_tab:
                # Open in new tab
                driver.execute_script(f"window.open('{url}', '_blank');")
                time.sleep(1)
                # Switch to new tab
                driver.switch_to.window(driver.window_handles[-1])
            else:
                # Open in current tab
                driver.get(url)
            
            # Wait for page to load
            self._wait_for_page_load()
            
            logger.info(f"Successfully navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def open_website(self, site_name, new_tab=False):
        """
        Open common website by name
        
        Args:
            site_name (str): Name of website (e.g., 'youtube', 'google')
            new_tab (bool): Open in new tab if True
        
        Returns:
            tuple: (success, url)
        """
        try:
            site_name = site_name.lower().strip()
            
            # Check if it's a common site
            if site_name in self.common_sites:
                url = self.common_sites[site_name]
                logger.info(f"Opening {site_name}: {url}")
                success = self.goto_url(url, new_tab=new_tab)
                return success, url
            
            # Check if it's a domain (contains .com, .in, .org, etc.)
            elif '.' in site_name:
                logger.info(f"Opening custom website: {site_name}")
                success = self.goto_url(site_name, new_tab=new_tab)
                return success, site_name
            
            # Try adding .com
            else:
                url = f"{site_name}.com"
                logger.info(f"Trying: {url}")
                success = self.goto_url(url, new_tab=new_tab)
                return success, url
                
        except Exception as e:
            logger.error(f"Failed to open website {site_name}: {e}")
            return False, None
    
    def search_google(self, query, new_tab=False):
        """
        Search on Google
        
        Args:
            query (str): Search query
            new_tab (bool): Open in new tab if True
        
        Returns:
            bool: True if successful
        """
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            logger.info(f"Searching Google for: {query}")
            return self.goto_url(search_url, new_tab=new_tab)
            
        except Exception as e:
            logger.error(f"Failed to search on Google: {e}")
            return False
    
    def _wait_for_page_load(self, timeout=10):
        """
        Wait for page to load completely
        
        Args:
            timeout (int): Maximum wait time in seconds
        """
        try:
            driver = self.browser.get_driver()
            if driver:
                WebDriverWait(driver, timeout).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                time.sleep(1)  # Additional buffer
                logger.info("Page loaded successfully")
        except TimeoutException:
            logger.warning("Page load timeout")
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")
    
    def get_page_info(self):
        """
        Get current page information
        
        Returns:
            dict: Page title and URL
        """
        try:
            return {
                'title': self.browser.get_page_title(),
                'url': self.browser.get_current_url()
            }
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return {'title': None, 'url': None}
    
    def go_back(self):
        """Go back to previous page"""
        try:
            driver = self.browser.get_driver()
            if driver:
                driver.back()
                self._wait_for_page_load()
                logger.info("Navigated back")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to go back: {e}")
            return False
    
    def go_forward(self):
        """Go forward to next page"""
        try:
            driver = self.browser.get_driver()
            if driver:
                driver.forward()
                self._wait_for_page_load()
                logger.info("Navigated forward")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to go forward: {e}")
            return False
    
    def refresh_page(self):
        """Refresh current page"""
        try:
            driver = self.browser.get_driver()
            if driver:
                driver.refresh()
                self._wait_for_page_load()
                logger.info("Page refreshed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to refresh: {e}")
            return False