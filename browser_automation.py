import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
from utils import random_wait, ensure_dir_exists

pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort

logger = logging.getLogger(__name__)

class SunoAutomation:
    """Class to automate interactions with Suno.ai"""
    
    def __init__(self, email=None, password=None, headless=False, use_chrome_profile=False, chrome_user_data_dir=None):
        self.email = email
        self.password = password
        self.logged_in = False
        self.headless = headless
        self.use_chrome_profile = use_chrome_profile
        self.chrome_user_data_dir = chrome_user_data_dir
        self.driver = self._setup_driver()
        
    def _setup_driver(self):
        """Set up and configure the Chrome WebDriver"""
        logger.info("Setting up Chrome driver")
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Use Chrome profile if specified
        if self.use_chrome_profile and self.chrome_user_data_dir:
            logger.info(f"Using Chrome profile from: {self.chrome_user_data_dir}")
            chrome_options.add_argument(f"user-data-dir={self.chrome_user_data_dir}")
            chrome_options.add_argument("profile-directory=Default")
        
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def _human_type(self, element, text):
        """Type text like a human with random delays"""
        for char in text:
            element.send_keys(char)
            # Random delay between keystrokes (50-200ms)
            time.sleep(random.uniform(0.05, 0.2))
    
    def _human_move_and_click(self, element):
        """Move mouse and click like a human"""
        # Get element position
        location = element.location
        size = element.size
        
        # Calculate center of element
        x = location['x'] + size['width'] // 2
        y = location['y'] + size['height'] // 2
        
        # Current mouse position
        current_x, current_y = pyautogui.position()
        
        # Calculate intermediate points for natural movement
        steps = random.randint(10, 20)
        for i in range(steps):
            next_x = current_x + (x - current_x) * (i + 1) / steps
            next_y = current_y + (y - current_y) * (i + 1) / steps
            
            # Add slight randomness to path
            next_x += random.randint(-10, 10)
            next_y += random.randint(-10, 10)
            
            pyautogui.moveTo(next_x, next_y, duration=0.1)
        
        # Move to exact position and click with random delay
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(random.uniform(0.1, 0.3))
        pyautogui.click()
    
    def login(self):
        """Login to Suno.ai"""
        if self.logged_in:
            logger.info("Already logged in")
            return True
        
        logger.info("Navigating to Suno.ai")
        self.driver.get("https://suno.ai")
        
        try:
            # If using Chrome profile, check if already logged in
            if self.use_chrome_profile:
                try:
                    # Check for elements that indicate we're logged in - looking for Create button
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'New')]"))
                    )
                    logger.info("Already logged in via Chrome profile")
                    self.logged_in = True
                    return True
                except TimeoutException:
                    logger.info("Not logged in via Chrome profile, proceeding with Google login")
                    
                    # Find and click the Google login button
                    try:
                        # Look for Google login button
                        google_login = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue with Google') or contains(@class, 'google')]"))
                        )
                        logger.info("Clicking Google login button")
                        self._human_move_and_click(google_login)
                        
                        # Since we're using Chrome profile, Google might auto-login
                        # Give it time to process the Google authentication
                        logger.info("Waiting for Google authentication to complete...")
                        time.sleep(10)
                        
                        # Check if we're logged in
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'New')]"))
                        )
                        
                        logger.info("Successfully logged in with Google")
                        self.logged_in = True
                        return True
                    except Exception as e:
                        logger.error(f"Google login failed: {str(e)}")
                        return False
            
            # Traditional login path (email/password)
            if not self.use_chrome_profile and self.email and self.password:
                # Wait for login button and click it
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]"))
                )
                logger.info("Clicking login button")
                self._human_move_and_click(login_button)
                
                # Wait for email field and enter email
                email_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email']"))
                )
                logger.info("Entering email")
                self._human_type(email_field, self.email)
                
                # Wait for password field and enter password
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password']"))
                )
                logger.info("Entering password")
                self._human_type(password_field, self.password)
                
                # Click submit button
                submit_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(text(), 'Sign in') or contains(text(), 'Log in')]"))
                )
                logger.info("Submitting login form")
                self._human_move_and_click(submit_button)
            else:
                # Give user time to complete Google login if needed
                logger.info("Waiting for user to complete Google login via Chrome profile...")
                time.sleep(15)  # Adjust timeout as needed
            
            # Wait for successful login (check for create button or user profile)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'New')]"))
            )
            
            logger.info("Successfully logged in")
            self.logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def generate_song(self, prompt):
        """Generate a song with the given prompt"""
        logger.info(f"Generating song with prompt: {prompt}")
        
        if not self.logged_in:
            if not self.login():
                return {"success": False, "error": "Login failed"}
        
        try:
            # Navigate to create page if not already there
            if "create" not in self.driver.current_url:
                self.driver.get("https://suno.ai/create")
                time.sleep(2)  # Wait for page to load
            
            # Find and click on the prompt input field
            prompt_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//textarea[contains(@placeholder, 'prompt') or contains(@placeholder, 'describe')]"))
            )
            self._human_move_and_click(prompt_field)
            
            # Clear any existing text and enter new prompt
            prompt_field.clear()
            self._human_type(prompt_field, prompt)
            
            # Click the generate/create button
            generate_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate') or contains(text(), 'Create')]"))
            )
            logger.info("Clicking generate button")
            self._human_move_and_click(generate_button)
            
            # Wait for generation to complete - look for download button or share link
            logger.info("Waiting for song generation to complete...")
            
            # Wait for the generating indicator to disappear
            try:
                WebDriverWait(self.driver, 300).until_not(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Generating') or contains(text(), 'Processing')]"))
                )
            except TimeoutException:
                logger.warning("Generation might still be in progress, but continuing...")
            
            # Wait for share or download buttons to appear
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Share') or contains(text(), 'Download')]"))
            )
            
            logger.info("Song generation completed")
            
            # Get the song URL - this depends on Suno's interface
            try:
                # Try to find a share button and click it
                share_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')]"))
                )
                self._human_move_and_click(share_button)
                
                # Wait for URL input field or element containing URL to appear
                url_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[contains(@value, 'suno.ai')]"))
                )
                song_url = url_element.get_attribute("value")
                
                # Close share dialog if needed
                try:
                    close_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Close')]")
                    self._human_move_and_click(close_button)
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Couldn't get share link: {e}")
                # Fallback: use current URL
                song_url = self.driver.current_url
            
            return {"success": True, "url": song_url, "prompt": prompt}
            
        except Exception as e:
            logger.error(f"Song generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def download_song(self, song_url=None):
        """Download the generated song"""
        logger.info("Attempting to download song")
        
        try:
            if song_url:
                self.driver.get(song_url)
                time.sleep(3)  # Wait for page to load
            
            # Look for download button
            download_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')]"))
            )
            self._human_move_and_click(download_button)
            
            # Wait for download to start (can't easily detect when it finishes)
            time.sleep(5)
            
            # Get the most recently downloaded file in the Downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            files = sorted(
                [os.path.join(downloads_path, f) for f in os.listdir(downloads_path)],
                key=os.path.getctime
            )
            
            if files:
                latest_file = files[-1]
                if latest_file.endswith('.mp3') and (time.time() - os.path.getctime(latest_file)) < 10:
                    logger.info(f"Song downloaded to {latest_file}")
                    return {"success": True, "file_path": latest_file}
            
            return {"success": False, "error": "Downloaded file not found"}
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the browser and clean up"""
        logger.info("Closing browser")
        if hasattr(self, 'driver'):
            self.driver.quit()
