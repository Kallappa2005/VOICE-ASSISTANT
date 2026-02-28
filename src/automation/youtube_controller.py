"""
YouTube Controller
Handles YouTube-specific automation tasks
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.core.logger import setup_logger
import time

logger = setup_logger(__name__)

class YouTubeController:
    """Controls YouTube automation"""
    
    def __init__(self, browser_controller):
        """
        Initialize YouTube controller
        
        Args:
            browser_controller: BrowserController instance
        """
        self.browser = browser_controller
        self.youtube_url = "https://www.youtube.com"
        logger.info("YouTube controller initialized")
    
    def open_youtube(self):
        """
        Open YouTube homepage
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Opening YouTube")
            driver.get(self.youtube_url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check if YouTube loaded
            if "youtube" in driver.current_url.lower():
                logger.info("YouTube opened successfully")
                return True
            else:
                logger.error("Failed to open YouTube")
                return False
            
        except Exception as e:
            logger.error(f"Failed to open YouTube: {e}")
            return False
    
    def search_video(self, query):
        """
        Search for videos on YouTube
        
        Args:
            query (str): Search query
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            # Ensure we're on YouTube
            if "youtube" not in driver.current_url.lower():
                self.open_youtube()
                time.sleep(2)
            
            logger.info(f"Searching YouTube for: {query}")
            
            # Find search box - YouTube uses multiple possible selectors
            search_box = None
            search_selectors = [
                (By.NAME, "search_query"),
                (By.ID, "search"),
                (By.CSS_SELECTOR, "input#search"),
                (By.CSS_SELECTOR, "input[name='search_query']"),
                (By.XPATH, "//input[@id='search']")
            ]
            
            for by, selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info(f"Found search box using: {by}={selector}")
                    break
                except TimeoutException:
                    continue
            
            if not search_box:
                logger.error("Could not find YouTube search box")
                return False
            
            # Clear and enter search query
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys(query)
            time.sleep(1)
            
            # Press Enter to search
            search_box.send_keys(Keys.RETURN)
            logger.info("Search query submitted")
            
            # Wait for results to load
            time.sleep(3)
            
            # Verify results loaded
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "video-title"))
                )
                logger.info("Search results loaded successfully")
                return True
            except TimeoutException:
                logger.warning("Search results took too long to load")
                return True  # Still return True as search was submitted
            
        except Exception as e:
            logger.error(f"Failed to search YouTube: {e}")
            return False
    
    def get_search_results_count(self):
        """
        Get approximate number of visible search results
        
        Returns:
            int: Number of video results found
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return 0
            
            # Find video title elements
            video_elements = driver.find_elements(By.ID, "video-title")
            count = len(video_elements)
            
            logger.info(f"Found {count} video results")
            return count
            
        except Exception as e:
            logger.error(f"Failed to count results: {e}")
            return 0
    
    def get_first_video_title(self):
        """
        Get title of first search result
        
        Returns:
            str: Video title or None
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return None
            
            # Find first video title
            video_title = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "video-title"))
            )
            
            title = video_title.get_attribute("title") or video_title.text
            logger.info(f"First video: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Failed to get first video title: {e}")
            return None
    
    def click_first_video(self):
        """
        Click on first search result to play video
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Clicking first video")
            
            # Find and click first video
            video_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "video-title"))
            )
            
            video_title = video_link.get_attribute("title") or video_link.text
            logger.info(f"Clicking video: {video_title}")
            
            video_link.click()
            
            # Wait for video page to load
            time.sleep(3)
            
            # Verify we're on video page
            if "/watch?v=" in driver.current_url:
                logger.info("Video page loaded successfully")
                return True
            else:
                logger.warning("May not be on video page")
                return False
            
        except Exception as e:
            logger.error(f"Failed to click first video: {e}")
            return False
    
    def is_on_youtube(self):
        """
        Check if currently on YouTube
        
        Returns:
            bool: True if on YouTube
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return False
            
            return "youtube" in driver.current_url.lower()
            
        except Exception as e:
            logger.error(f"Error checking YouTube status: {e}")
            return False
    
    def get_current_video_title(self):
        """
        Get title of currently playing video
        
        Returns:
            str: Video title or None
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return None
            
            # Multiple selectors for video title
            title_selectors = [
                (By.CSS_SELECTOR, "h1.title yt-formatted-string"),
                (By.CSS_SELECTOR, "h1.ytd-video-primary-info-renderer"),
                (By.XPATH, "//h1[@class='title']//yt-formatted-string"),
                (By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-video-primary-info-renderer")
            ]
            
            for by, selector in title_selectors:
                try:
                    title_element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    title = title_element.text
                    if title:
                        logger.info(f"Current video: {title}")
                        return title
                except:
                    continue
            
            logger.warning("Could not find video title")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get current video title: {e}")
            return None