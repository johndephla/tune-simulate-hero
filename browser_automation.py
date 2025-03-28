import time
import random
import logging
import os
import platform
import tempfile
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import pyautogui
from utils import random_wait, ensure_dir_exists

pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort

logger = logging.getLogger(__name__)

class SunoAutomation:
    """Class to automate interactions with Suno.com"""
    
    def __init__(self, email=None, password=None, headless=False, use_chrome_profile=False, chrome_user_data_dir=None):
        self.email = email
        self.password = password
        self.logged_in = False
        self.headless = headless
        self.use_chrome_profile = use_chrome_profile
        self.chrome_user_data_dir = chrome_user_data_dir
        self.driver = None
        self.connected = False
        self.connection_error = None
        
        try:
            self.driver = self._setup_driver()
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            self.connection_error = str(e)
            self.connected = False
        
    def _setup_driver(self):
        """Set up and configure the Chrome WebDriver"""
        try:
            # Set up Chrome options
            chrome_options = Options()
            
            # Disable automation controlled banner
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set user agent to mimic a real user
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36"
            chrome_options.add_argument(f"user-agent={user_agent}")
            
            # Handle Chrome profile
            if self.use_chrome_profile:
                if self.chrome_user_data_dir:
                    chrome_options.add_argument(f"user-data-dir={self.chrome_user_data_dir}")
                    logger.info(f"Using Chrome profile from: {self.chrome_user_data_dir}")
                else:
                    logger.warning("Chrome profile directory not specified, using default")
            
            # Set headless mode if specified
            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")  # Necessary for some systems
                chrome_options.add_argument("--window-size=1920x1080")  # Set window size for headless mode
            
            # Disable logging to file
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            
            # Add additional options for security and stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-popup-blocking")
            
            # Set download directory to a temporary directory
            download_dir = tempfile.mkdtemp()
            prefs = {"download.default_directory": download_dir,
                     "download.prompt_for_download": False,
                     "download.directory_upgrade": True,
                     "safebrowsing.enabled": False}  # Disable safe browsing to prevent download issues
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Initialize ChromeDriver using ChromeDriverManager
            try:
                # Specify the desired Chrome type (Chrome or Chromium)
                if platform.system() == "Darwin":
                    # On macOS, use Chromium to avoid compatibility issues
                    chrome_type = ChromeType.CHROMIUM
                else:
                    chrome_type = ChromeType.GOOGLE
                
                driver_manager = ChromeDriverManager(chrome_type=chrome_type)
                service = Service(driver_manager.install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("ChromeDriver initialized with ChromeDriverManager")
            except Exception as e:
                logger.error(f"Failed to initialize ChromeDriver with ChromeDriverManager: {str(e)}")
                logger.info("Attempting to use ChromeDriver from system PATH")
                try:
                    service = Service()  # Assumes ChromeDriver is in PATH
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("ChromeDriver initialized from system PATH")
                except Exception as ex:
                    logger.error(f"Failed to initialize ChromeDriver from system PATH: {str(ex)}")
                    raise ex  # Re-raise the exception to be caught in the main block
            
            # Set an implicit wait for elements to load
            driver.implicitly_wait(10)
            
            # Maximize window (if not headless)
            if not self.headless:
                driver.maximize_window()
            
            return driver
        except Exception as e:
            logger.error(f"Driver setup failed: {str(e)}")
            raise e
    
    def is_connected(self):
        """Check if browser is connected and working"""
        if not self.driver:
            return False
        
        try:
            # Just access a property to check if driver is still responsive
            current_url = self.driver.current_url
            return True
        except:
            self.connected = False
            return False
    
    def get_status(self):
        """Get current status of the browser automation"""
        return {
            "connected": self.connected and self.is_connected(),
            "logged_in": self.logged_in,
            "error": self.connection_error
        }
    
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
        """Login to Suno.com"""
        if not self.connected or not self.driver:
            logger.error("Browser not connected, can't login")
            return False
            
        if self.logged_in:
            logger.info("Already logged in")
            return True
        
        logger.info("Navigating to Suno.com")
        try:
            # Updated URL to use the new domain and dashboard path
            self.driver.get("https://suno.com/create?wid=default")
            
            # Take a debug screenshot
            screenshot_path = os.path.join(os.path.expanduser("~"), "suno_debug_login.png")
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Login page screenshot saved to {screenshot_path}")
            
            # Check for any prompt textarea which indicates we're already logged in
            try:
                # Look for textarea element - this is the main prompt field
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
                )
                logger.info("Already logged in via Chrome profile")
                self.logged_in = True
                return True
            except TimeoutException:
                logger.info("Not logged in yet, proceeding with authentication")
            
            # If using Chrome profile, check if already logged in or try to log in
            if self.use_chrome_profile:
                try:
                    # Look for login/sign-in button
                    login_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Log in') or contains(text(), 'Sign in')]"
                    )
                    
                    if login_buttons:
                        logger.info("Clicking Log in button")
                        self._human_move_and_click(login_buttons[0])
                        time.sleep(2)
                    
                    # Look for Google login button
                    google_login = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, 
                            "//button[contains(text(), 'Google') or contains(@class, 'google')]"
                        ))
                    )
                    logger.info("Clicking Google login button")
                    self._human_move_and_click(google_login)
                    
                    # Since we're using Chrome profile, Google might auto-login
                    # Give it time to process the Google authentication
                    logger.info("Waiting for Google authentication to complete...")
                    time.sleep(10)
                    
                    # Check if we're logged in by looking for the textarea elements
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
                    )
                    
                    logger.info("Successfully logged in with Google")
                    self.logged_in = True
                    return True
                except Exception as e:
                    logger.error(f"Google login failed: {str(e)}")
                    # Continue to try email/password or manual login below
            
            # Traditional login path (email/password)
            if not self.use_chrome_profile and self.email and self.password:
                try:
                    # Click the login button
                    login_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Log in') or contains(text(), 'Sign in')]"
                    )
                    
                    if login_buttons:
                        logger.info("Clicking Log in button")
                        self._human_move_and_click(login_buttons[0])
                        time.sleep(2)
                    
                    # Try to find the email login option
                    email_option = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Email')]")
                    if email_option:
                        logger.info("Clicking Email login option")
                        self._human_move_and_click(email_option[0])
                        time.sleep(2)
                    
                    # Wait for email field and enter email
                    email_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email']"))
                    )
                    logger.info("Entering email")
                    self._human_type(email_field, self.email)
                    
                    # Find continue button and click it
                    continue_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Continue')]")
                    if continue_buttons:
                        logger.info("Clicking Continue button")
                        self._human_move_and_click(continue_buttons[0])
                        time.sleep(2)
                    
                    # Wait for password field and enter password
                    password_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password']"))
                    )
                    logger.info("Entering password")
                    self._human_type(password_field, self.password)
                    
                    # Click submit/login button
                    submit_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Log in') or contains(text(), 'Sign in')]"
                    )
                    if submit_buttons:
                        logger.info("Clicking final login button")
                        self._human_move_and_click(submit_buttons[0])
                    
                    logger.info("Waiting for successful login...")
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Email/password login steps failed: {str(e)}")
            else:
                # Give user time to complete login if needed
                logger.info("Waiting for user to complete login manually...")
                time.sleep(15)
            
            # Final check - wait for the presence of textarea to confirm login
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
            )
            
            logger.info("Successfully logged in")
            self.logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.connection_error = f"Login failed: {str(e)}"
            self.logged_in = False
            return False
    
    def generate_song(self, prompt, style=None, title=None, instrumental=True):
        """Generate a song with the given parameters"""
        if not self.connected or not self.driver:
            logger.error("Browser not connected, can't generate song")
            return {"success": False, "error": "Browser not connected"}
            
        logger.info(f"Generating song with prompt: {prompt}, style: {style}, title: {title}, instrumental: {instrumental}")
        
        if not self.logged_in:
            if not self.login():
                return {"success": False, "error": "Login failed"}
        
        try:
            # Navigate to create page if not already there
            if "create" not in self.driver.current_url:
                self.driver.get("https://suno.com/create?wid=default")
                time.sleep(3)
                logger.info("Navigated to the create page")
            
            # Take a debug screenshot
            screenshot_path = os.path.join(os.path.expanduser("~"), "suno_debug_create.png")
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Create page screenshot saved to {screenshot_path}")
            
            # Using the provided CSS selectors to interact with UI elements
            try:
                # Find and enter the main prompt textarea - this is the large textarea at the bottom
                # Since we don't have a specific selector for it, we'll try to find all textareas and use the largest one
                textareas = self.driver.find_elements(By.CSS_SELECTOR, "textarea")
                main_textarea = None
                
                # Find the textarea that takes most of the space or has no specific placeholder
                # It's likely to be the main prompt area
                for textarea in textareas:
                    if not textarea.get_attribute("placeholder") or "Enter" in textarea.get_attribute("placeholder"):
                        main_textarea = textarea
                        break
                
                if not main_textarea and textareas:
                    # If we can't identify specifically, take the last textarea which is often the main one
                    main_textarea = textareas[-1]
                
                if main_textarea:
                    logger.info("Found main prompt textarea")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", main_textarea)
                    time.sleep(1)
                    self._human_move_and_click(main_textarea)
                    main_textarea.clear()
                    self._human_type(main_textarea, prompt)
                    logger.info("Entered prompt text")
                else:
                    logger.error("Could not find main prompt textarea")
                    return {"success": False, "error": "Could not find prompt textarea"}
                
                # Handle style input using the specific selector provided
                if style:
                    try:
                        style_textarea = self.driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder="Enter style of music"]')
                        logger.info(f"Found style textarea with specific selector, entering: {style}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", style_textarea)
                        time.sleep(1)
                        self._human_move_and_click(style_textarea)
                        style_textarea.clear()
                        self._human_type(style_textarea, style)
                    except NoSuchElementException:
                        logger.warning("Style textarea not found with specific selector, trying alternative methods")
                        # Try alternative methods to find the style input
                        try:
                            style_textareas = self.driver.find_elements(By.XPATH, 
                                "//span[contains(text(), 'Style of Music')]/following::textarea"
                            )
                            if style_textareas:
                                logger.info(f"Found style input through text search, entering: {style}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", style_textareas[0])
                                time.sleep(1)
                                self._human_move_and_click(style_textareas[0])
                                style_textareas[0].clear()
                                self._human_type(style_textareas[0], style)
                        except Exception as e:
                            logger.warning(f"Alternative style input method failed: {e}")
                
                # Handle title input using the specific selector provided
                if title:
                    try:
                        title_input = self.driver.find_element(By.CSS_SELECTOR, 'textarea[placeholder="Enter a title"]')
                        logger.info(f"Found title input with specific selector, entering: {title}")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", title_input)
                        time.sleep(1)
                        self._human_move_and_click(title_input)
                        title_input.clear()
                        self._human_type(title_input, title)
                    except NoSuchElementException:
                        logger.warning("Title input not found with specific selector, trying alternative methods")
                        try:
                            title_elements = self.driver.find_elements(By.XPATH, 
                                "//span[contains(text(), 'Title')]/following::textarea"
                            )
                            if title_elements:
                                logger.info(f"Found title input through text search, entering: {title}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", title_elements[0])
                                time.sleep(1)
                                self._human_move_and_click(title_elements[0])
                                title_elements[0].clear()
                                self._human_type(title_elements[0], title)
                        except Exception as e:
                            logger.warning(f"Alternative title input method failed: {e}")
                
                # Handle instrumental toggle using the specific selector provided
                if instrumental is not None:
                    try:
                        # First check if the toggle exists
                        toggle_container = self.driver.find_element(By.CSS_SELECTOR, 'div[aria-label="Instrumental"]')
                        logger.info("Found instrumental toggle container with specific selector")
                        
                        # Check if it's already in the correct state
                        toggle_span = toggle_container.find_element(By.CSS_SELECTOR, "span")
                        is_active = "translate-x-4" in toggle_span.get_attribute("class")
                        
                        logger.info(f"Instrumental toggle current state: {'active' if is_active else 'inactive'}")
                        
                        # Click only if we need to change the state
                        if is_active != instrumental:
                            logger.info(f"Clicking instrumental toggle to change from {is_active} to {instrumental}")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", toggle_container)
                            time.sleep(1)
                            self._human_move_and_click(toggle_container)
                            time.sleep(1)
                        else:
                            logger.info(f"Instrumental toggle already in desired state: {instrumental}")
                    except NoSuchElementException:
                        logger.warning("Instrumental toggle not found with specific selector, trying alternative methods")
                        try:
                            # Alternative approach using text nearby
                            toggle_elements = self.driver.find_elements(By.XPATH, 
                                "//span[contains(text(), 'Instrumental')]/preceding::div[@aria-label and contains(@class, 'inline-flex')]"
                            )
                            if toggle_elements:
                                toggle = toggle_elements[0]
                                
                                # Try to determine current state
                                toggle_class = toggle.get_attribute("class")
                                is_active = "translate-x-4" in toggle_class
                                
                                if is_active != instrumental:
                                    logger.info(f"Clicking alternative instrumental toggle to change from {is_active} to {instrumental}")
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", toggle)
                                    time.sleep(1)
                                    self._human_move_and_click(toggle)
                                    time.sleep(1)
                        except Exception as e:
                            logger.warning(f"Alternative instrumental toggle method failed: {e}")
                
                # Take a screenshot after setting all parameters
                self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_params_set.png"))
                
                # Find and click the generate/create button - using multiple approaches
                create_button = None
                
                # Try to find the Create button with class buttonAnimate first (new UI)
                try:
                    create_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.buttonAnimate")
                    for button in create_buttons:
                        if button.is_displayed() and "Create" in button.text:
                            create_button = button
                            break
                except:
                    logger.warning("Could not find Create button with buttonAnimate class")
                
                # If not found, try other methods
                if not create_button:
                    button_locators = [
                        (By.XPATH, "//button[contains(text(), 'Create')]"),
                        (By.XPATH, "//button[.//span[contains(text(), 'Create')]]"),
                        (By.CSS_SELECTOR, ".create-button button"),
                        (By.XPATH, "//div[contains(@class, 'create-button')]//button")
                    ]
                    
                    for by, locator in button_locators:
                        buttons = self.driver.find_elements(by, locator)
                        for button in buttons:
                            if button.is_displayed():
                                create_button = button
                                break
                        if create_button:
                            break
                
                if not create_button:
                    logger.error("Could not find the Create button")
                    return {"success": False, "error": "Could not find the Create button"}
                
                # Check if the button is enabled
                is_disabled = create_button.get_attribute("disabled")
                if is_disabled:
                    logger.warning("Create button is disabled. This could be due to input errors or account limitations.")
                    self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_disabled_button.png"))
                    return {"success": False, "error": "Create button is disabled. You may need to check inputs or account limitations."}
                
                # Scroll to the button
                self.driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
                time.sleep(1)
                
                # Take screenshot before clicking
                self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_before_click.png"))
                
                logger.info("Clicking Create button")
                self._human_move_and_click(create_button)
                
                # Wait for generation to start and complete
                logger.info("Waiting for song generation to begin...")
                
                # First, look for indicators that generation has started
                generation_started = False
                try:
                    generating_indicators = [
                        "//div[contains(text(), 'Creating')]", 
                        "//div[contains(text(), 'Generating')]",
                        "//div[contains(@class, 'loading')]",
                        "//div[contains(@class, 'spinner')]",
                        "//svg[contains(@class, 'spinner')]",
                        "//div[contains(text(), 'Please wait')]"
                    ]
                    
                    for indicator in generating_indicators:
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, indicator))
                            )
                            generation_started = True
                            logger.info(f"Song generation started (detected indicator: {indicator})")
                            break
                        except TimeoutException:
                            continue
                except TimeoutException:
                    pass
                
                if not generation_started:
                    # If we didn't see a loading indicator, the song may have generated very quickly
                    # or we missed the indicator - we'll check for completion indicators anyway
                    logger.warning("Did not detect generation start indicators - continuing anyway")
                
                # Wait for indicators that generation is complete (player controls appearing)
                completion_indicators = [
                    "//button[contains(@aria-label, 'Play')]",
                    "//div[contains(@class, 'player')]",
                    "//audio",
                    "//button[contains(@aria-label, 'Download')]",
                    "//button[contains(text(), 'Download')]",
                    "//button[contains(text(), 'Share')]"
                ]
                
                generation_completed = False
                for indicator in completion_indicators:
                    try:
                        WebDriverWait(self.driver, 300).until(  # Wait up to 5 minutes
                            EC.presence_of_element_located((By.XPATH, indicator))
                        )
                        generation_completed = True
                        logger.info(f"Song generation completed (detected indicator: {indicator})")
                        break
                    except TimeoutException:
                        continue
                
                if not generation_completed:
                    logger.error("Song generation timed out or failed")
                    return {"success": False, "error": "Song generation timed out"}
                
                # Take a final screenshot
                self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_complete.png"))
                
                # Get the song URL
                song_url = self.driver.current_url
                logger.info(f"Generated song URL: {song_url}")
                
                return {
                    "success": True, 
                    "url": song_url, 
                    "prompt": prompt, 
                    "style": style, 
                    "title": title
                }
                else:
                    logger.error("Could not find main prompt textarea")
                    return {"success": False, "error": "Could not find prompt textarea"}
            except Exception as e:
                logger.error(f"Failed to interact with creation form: {str(e)}")
                return {"success": False, "error": f"Failed to fill creation form: {str(e)}"}
                
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
            
            # Take a screenshot to debug download process
            self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_download.png"))
            
            # Look for download button - there are several ways it might appear in the UI
            download_selectors = [
                "//button[contains(text(), 'Download')]", 
                "//button[contains(@aria-label, 'Download')]",
                "//div[contains(text(), 'Download')]",
                "//span[contains(text(), 'Download')]",
                "//button[.//span[contains(text(), 'Download')]]",
                "//a[contains(@download, '')]"  # Direct download links
            ]
            
            download_element = None
            for selector in download_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        download_element = element
                        break
                if download_element:
                    break
            
            if not download_element:
                logger.error("No download button found")
                return {"success": False, "error": "Download button not found"}
                
            logger.info(f"Found download element, attempting to click")
            
            # Scroll to the download element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", download_element)
            time.sleep(1)
            
            # Click the download button
            self._human_move_and_click(download_element)
            
            # Wait for download to start
            time.sleep(5)
            
            # Get the most recently downloaded file in the Downloads folder
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            files = sorted(
                [os.path.join(downloads_path, f) for f in os.listdir(downloads_path)],
                key=os.path.getctime
            )
            
            if files:
                latest_file = files[-1]
                if (latest_file.endswith('.mp3') or latest_file.endswith('.wav')) and (time.time() - os.path.getctime(latest_file)) < 10:
                    logger.info(f"Song downloaded to {latest_file}")
                    return {"success": True, "file_path": latest_file}
            
            return {"success": False, "error": "Downloaded file not found"}
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the browser and clean up"""
        logger.info("Closing browser")
        if self.connected and hasattr(self, 'driver'):
            try:
                self.driver.quit()
            except:
                pass
            
        self.connected = False
        self.logged_in = False
