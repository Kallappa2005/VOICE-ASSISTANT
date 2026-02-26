"""
Tab Manager
Handles browser tab operations like closing, switching, and managing multiple tabs
"""

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from src.core.logger import setup_logger
import time

logger = setup_logger(__name__)

class TabManager:
    """Manages browser tabs"""
    
    def __init__(self, browser_controller):
        """
        Initialize tab manager
        
        Args:
            browser_controller: BrowserController instance
        """
        self.browser = browser_controller
        logger.info("Tab manager initialized")
    
    def close_current_tab(self):
        """
        Close the current active tab
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            # Get current tab count
            all_handles = driver.window_handles
            initial_tabs = len(all_handles)
            
            if initial_tabs == 1:
                logger.warning("Only one tab open - will close browser")
                return self.browser.close_browser()
            
            logger.info(f"Closing current tab (Total tabs: {initial_tabs})")
            
            # Get current handle
            current_handle = driver.current_window_handle
            current_index = all_handles.index(current_handle)
            
            # Close current tab
            driver.close()
            
            time.sleep(0.5)
            
            # Switch to next available tab
            remaining_handles = driver.window_handles
            
            if remaining_handles:
                # Switch to previous tab if we closed the last one
                if current_index >= len(remaining_handles):
                    driver.switch_to.window(remaining_handles[-1])
                else:
                    driver.switch_to.window(remaining_handles[current_index])
                
                final_tabs = len(remaining_handles)
                logger.info(f"Tab closed successfully (Remaining tabs: {final_tabs})")
                return True
            else:
                logger.info("All tabs closed")
                return True
            
        except Exception as e:
            logger.error(f"Failed to close tab: {e}")
            return False
    
    def close_all_tabs(self):
        """
        Close all tabs and browser
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Closing all tabs and browser")
            return self.browser.close_browser()
            
        except Exception as e:
            logger.error(f"Failed to close all tabs: {e}")
            return False
    
    def open_new_tab(self, url=None):
        """
        Open a new tab
        
        Args:
            url (str): Optional URL to open in new tab
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Opening new tab")
            
            # Open new tab using JavaScript
            if url:
                driver.execute_script(f"window.open('{url}', '_blank');")
                logger.info(f"Opened new tab with URL: {url}")
            else:
                driver.execute_script("window.open('about:blank', '_blank');")
                logger.info("Opened blank new tab")
            
            time.sleep(1)
            
            # Switch to new tab (last one)
            driver.switch_to.window(driver.window_handles[-1])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to open new tab: {e}")
            return False
    
    def switch_to_next_tab(self):
        """
        Switch to next tab (right)
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            all_handles = driver.window_handles
            if len(all_handles) <= 1:
                logger.warning("Only one tab open")
                return False
            
            # Get current tab index
            current_handle = driver.current_window_handle
            current_index = all_handles.index(current_handle)
            
            # Calculate next index (wrap around)
            next_index = (current_index + 1) % len(all_handles)
            
            logger.info(f"Switching from tab {current_index} to tab {next_index}")
            
            # Switch to next tab
            driver.switch_to.window(all_handles[next_index])
            
            time.sleep(0.5)
            logger.info(f"Switched to tab {next_index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to next tab: {e}")
            return False
    
    def switch_to_previous_tab(self):
        """
        Switch to previous tab (left)
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            all_handles = driver.window_handles
            if len(all_handles) <= 1:
                logger.warning("Only one tab open")
                return False
            
            # Get current tab index
            current_handle = driver.current_window_handle
            current_index = all_handles.index(current_handle)
            
            # Calculate previous index (wrap around)
            previous_index = (current_index - 1) % len(all_handles)
            
            logger.info(f"Switching from tab {current_index} to tab {previous_index}")
            
            # Switch to previous tab
            driver.switch_to.window(all_handles[previous_index])
            
            time.sleep(0.5)
            logger.info(f"Switched to tab {previous_index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to previous tab: {e}")
            return False
    
    def switch_to_tab(self, index):
        """
        Switch to specific tab by index
        
        Args:
            index (int): Tab index (0-based)
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            tabs = driver.window_handles
            
            if index < 0 or index >= len(tabs):
                logger.error(f"Invalid tab index: {index} (Total tabs: {len(tabs)})")
                return False
            
            logger.info(f"Switching to tab {index}")
            driver.switch_to.window(tabs[index])
            
            time.sleep(0.5)
            logger.info(f"Switched to tab {index}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to tab {index}: {e}")
            return False
    
    def get_tab_count(self):
        """
        Get number of open tabs
        
        Returns:
            int: Number of tabs or 0 if failed
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return 0
            
            count = len(driver.window_handles)
            logger.info(f"Current tab count: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Failed to get tab count: {e}")
            return 0
    
    def get_current_tab_index(self):
        """
        Get index of current active tab
        
        Returns:
            int: Tab index or -1 if failed
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return -1
            
            current_handle = driver.current_window_handle
            all_handles = driver.window_handles
            
            index = all_handles.index(current_handle)
            logger.info(f"Current tab index: {index}")
            return index
            
        except Exception as e:
            logger.error(f"Failed to get current tab index: {e}")
            return -1
    
    def close_tab_by_index(self, index):
        """
        Close specific tab by index
        
        Args:
            index (int): Tab index to close
        
        Returns:
            bool: True if successful
        """
        try:
            # Switch to tab first
            if self.switch_to_tab(index):
                # Then close it
                return self.close_current_tab()
            return False
            
        except Exception as e:
            logger.error(f"Failed to close tab {index}: {e}")
            return False
    
    def get_all_tab_titles(self):
        """
        Get titles of all open tabs
        
        Returns:
            list: List of tab titles
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return []
            
            current_handle = driver.current_window_handle
            titles = []
            
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                time.sleep(0.3)  # Small delay for title to load
                titles.append(driver.title)
            
            # Switch back to original tab
            driver.switch_to.window(current_handle)
            
            logger.info(f"Retrieved {len(titles)} tab titles")
            return titles
            
        except Exception as e:
            logger.error(f"Failed to get tab titles: {e}")
            return []