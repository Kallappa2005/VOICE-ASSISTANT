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
    
    def get_video_title_by_index(self, index):
        """
        Get title of video at specific index
        
        Args:
            index (int): Video index (0-based)
        
        Returns:
            str: Video title or None
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return None
            
            video_elements = driver.find_elements(By.ID, "video-title")
            
            if index < 0 or index >= len(video_elements):
                logger.error(f"Invalid index {index}, only {len(video_elements)} videos")
                return None
            
            title = video_elements[index].get_attribute("title") or video_elements[index].text
            logger.info(f"Video {index}: {title}")
            return title
            
        except Exception as e:
            logger.error(f"Failed to get video title at index {index}: {e}")
            return None
    def play_video_by_index(self, index):
        """
        Click and play video at specific index
        
        Args:
            index (int): Video index (0-based, so 0 = first video)
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info(f"Playing video at index {index}")
            
            # Get all video links
            video_elements = driver.find_elements(By.ID, "video-title")
            
            if index < 0 or index >= len(video_elements):
                logger.error(f"Invalid index {index}, only {len(video_elements)} videos available")
                return False
            
            # Get video element
            video_element = video_elements[index]
            
            # Get video title before clicking
            video_title = video_element.get_attribute("title") or video_element.text
            logger.info(f"Clicking video {index + 1}: {video_title}")
            
            # METHOD 1: Scroll element into center of viewport
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", video_element)
            time.sleep(1)
            
            # METHOD 2: Try JavaScript click if regular click fails
            try:
                # Try regular click first
                video_element.click()
                logger.info("Clicked video using regular click")
            except Exception as e1:
                logger.warning(f"Regular click failed: {e1}, trying JavaScript click")
                try:
                    # Use JavaScript click as fallback
                    driver.execute_script("arguments[0].click();", video_element)
                    logger.info("Clicked video using JavaScript")
                except Exception as e2:
                    logger.error(f"JavaScript click also failed: {e2}")
                    
                    # METHOD 3: Try clicking via href
                    try:
                        href = video_element.get_attribute("href")
                        if href:
                            logger.info(f"Navigating directly to URL: {href}")
                            driver.get(href)
                            logger.info("Navigated via URL")
                        else:
                            raise Exception("No href found")
                    except Exception as e3:
                        logger.error(f"URL navigation failed: {e3}")
                        return False
            
            # Wait for video page to load
            time.sleep(3)
            
            # Verify we're on video page
            if "/watch?v=" in driver.current_url:
                logger.info(f"Video page loaded: {video_title}")
                return True
            else:
                logger.warning("May not be on video page")
                return False
            
        except Exception as e:
            logger.error(f"Failed to play video at index {index}: {e}")
            return False  
    
    
    # def play_video_by_index(self, index):
    #     """
    #     Click and play video at specific index
        
    #     Args:
    #         index (int): Video index (0-based, so 0 = first video)
        
    #     Returns:
    #         bool: True if successful
    #     """
    #     try:
    #         driver = self.browser.get_driver()
    #         if not driver:
    #             logger.error("Browser not open")
    #             return False
            
    #         logger.info(f"Playing video at index {index}")
            
    #         # Get all video links
    #         video_elements = driver.find_elements(By.ID, "video-title")
            
    #         if index < 0 or index >= len(video_elements):
    #             logger.error(f"Invalid index {index}, only {len(video_elements)} videos available")
    #             return False
            
    #         # Get video title before clicking
    #         video_title = video_elements[index].get_attribute("title") or video_elements[index].text
    #         logger.info(f"Clicking video {index + 1}: {video_title}")
            
    #         # Scroll to video to ensure it's visible
    #         driver.execute_script("arguments[0].scrollIntoView(true);", video_elements[index])
    #         time.sleep(1)
            
    #         # Click the video
    #         video_elements[index].click()
            
    #         # Wait for video page to load
    #         time.sleep(3)
            
    #         # Verify we're on video page
    #         if "/watch?v=" in driver.current_url:
    #             logger.info(f"Video page loaded: {video_title}")
    #             return True
    #         else:
    #             logger.warning("May not be on video page")
    #             return False
            
    #     except Exception as e:
    #         logger.error(f"Failed to play video at index {index}: {e}")
    #         return False
    
    def click_first_video(self):
        """
        Click on first search result to play video
        
        Returns:
            bool: True if successful
        """
        return self.play_video_by_index(0)
    
    def pause_video(self):
        """
        Pause currently playing video
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Pausing video")
            
            # Check if video is already paused
            if not self.is_video_playing():
                logger.info("Video is already paused")
                return True
            
            # Click on video player to ensure focus
            try:
                video_player = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "video.html5-main-video"))
                )
                # Click to focus, but don't click the video itself (might toggle)
                # Just send key command
            except:
                logger.warning("Could not find video player")
            
            # Send 'k' key to pause (only if playing)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys('k')
            actions.perform()
            
            time.sleep(0.5)
            
            # Verify it paused
            if not self.is_video_playing():
                logger.info("Video paused successfully")
                return True
            else:
                logger.warning("Video may still be playing")
                return True
            
        except Exception as e:
            logger.error(f"Failed to pause video: {e}")
            return False
    
    def play_video(self):
        """
        Play/resume currently paused video
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Playing/resuming video")
            
            # Check if video is already playing
            if self.is_video_playing():
                logger.info("Video is already playing")
                return True
            
            # Click on video player to ensure focus
            try:
                video_player = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "video.html5-main-video"))
                )
            except:
                logger.warning("Could not find video player")
            
            # Send 'k' key to play (only if paused)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys('k')
            actions.perform()
            
            time.sleep(0.5)
            
            # Verify it's playing
            if self.is_video_playing():
                logger.info("Video playing successfully")
                return True
            else:
                logger.warning("Video may still be paused")
                return True
            
        except Exception as e:
            logger.error(f"Failed to play video: {e}")
            return False
    
    def stop_video(self):
        """
        Stop video (pause and seek to beginning)
        
        Returns:
            bool: True if successful
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                logger.error("Browser not open")
                return False
            
            logger.info("Stopping video")
            
            # First pause the video
            self.pause_video()
            time.sleep(0.5)
            
            # Seek to beginning (Home key or '0' key)
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.send_keys('0')  # '0' seeks to beginning
            actions.perform()
            
            time.sleep(0.5)
            logger.info("Video stopped and reset to beginning")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop video: {e}")
            return False
    
    def toggle_play_pause(self):
        """
        Toggle between play and pause
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Toggling play/pause")
            return self.pause_video()  # Same action for both
            
        except Exception as e:
            logger.error(f"Failed to toggle play/pause: {e}")
            return False
    
    def is_video_playing(self):
        """
        Check if video is currently playing
        
        Returns:
            bool: True if playing, False if paused or error
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return False
            
            # Check video element's paused property
            video_element = driver.find_element(By.CSS_SELECTOR, "video.html5-main-video")
            is_paused = driver.execute_script("return arguments[0].paused;", video_element)
            
            playing = not is_paused
            logger.info(f"Video playing status: {playing}")
            return playing
            
        except Exception as e:
            logger.error(f"Failed to check video status: {e}")
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
    
    def is_on_video_page(self):
        """
        Check if currently on a video watch page
        
        Returns:
            bool: True if on video page
        """
        try:
            driver = self.browser.get_driver()
            if not driver:
                return False
            
            return "/watch?v=" in driver.current_url
            
        except Exception as e:
            logger.error(f"Error checking video page: {e}")
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