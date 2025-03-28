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
        logger.info("Setting up Chrome driver")
        chrome_options = Options()
        
        if self.headless:
            logger.info("Running in headless mode")
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
        
        # Aggiungi argomenti per evitare problemi comuni
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # User agent specifico per evitare il rilevamento dell'automazione
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        # Use Chrome profile if specified
        if self.use_chrome_profile and self.chrome_user_data_dir:
            if not os.path.exists(self.chrome_user_data_dir):
                logger.warning(f"Chrome profile directory does not exist: {self.chrome_user_data_dir}")
                logger.info("Creating a new Chrome profile directory")
                try:
                    os.makedirs(self.chrome_user_data_dir, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create Chrome profile directory: {str(e)}")
                    raise Exception(f"Failed to create Chrome profile directory: {str(e)}")
            
            logger.info(f"Using Chrome profile from: {self.chrome_user_data_dir}")
            chrome_options.add_argument(f"user-data-dir={self.chrome_user_data_dir}")
            
            # Se siamo su Windows, verifichiamo se Chrome è in esecuzione
            if platform.system() == "Windows":
                try:
                    output = subprocess.check_output("tasklist | findstr chrome", shell=True)
                    logger.warning("Chrome is already running, this may cause issues with user-data-dir")
                except subprocess.CalledProcessError:
                    # Chrome non è in esecuzione, va bene
                    pass
        
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # Try multiple methods to initialize Chrome driver
        driver = None
        error_messages = []
        
        # Method 1: Using webdriver_manager (Auto-detect)
        try:
            logger.info("Method 1: Installing/updating ChromeDriver using webdriver_manager auto-detection")
            # Specify a custom cache path to avoid permission issues
            driver_cache_path = os.path.join(os.path.expanduser("~"), ".wdm", "drivers")
            os.makedirs(driver_cache_path, exist_ok=True)
            
            service = Service(ChromeDriverManager(path=driver_cache_path).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully with Method 1")
            
            # Impostazioni anti-detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            error_msg = f"Method 1 failed: {str(e)}"
            logger.warning(error_msg)
            error_messages.append(error_msg)
            
        # Method 2: Direct Chrome driver without service
        try:
            logger.info("Method 2: Using Chrome driver directly")
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully with Method 2")
            return driver
        except Exception as e:
            error_msg = f"Method 2 failed: {str(e)}"
            logger.warning(error_msg)
            error_messages.append(error_msg)
        
        # Method 3: Using the system's Chrome installation with webdriver_manager
        try:
            logger.info("Method 3: Using system Chrome with specific Chrome type")
            if platform.system() == "Windows":
                chrome_type = ChromeType.CHROMIUM
            else:
                chrome_type = ChromeType.GOOGLE
                
            service = Service(ChromeDriverManager(chrome_type=chrome_type).install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully with Method 3")
            return driver
        except Exception as e:
            error_msg = f"Method 3 failed: {str(e)}"
            logger.warning(error_msg)
            error_messages.append(error_msg)
        
        # Method 4: Specify a compatible Chrome driver version explicitly
        try:
            logger.info("Method 4: Specifying a compatible Chrome driver version explicitly")
            # Try with a specific version that might be compatible with many Chrome versions
            service = Service(ChromeDriverManager(version="113.0.5672.63").install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully with Method 4")
            return driver
        except Exception as e:
            error_msg = f"Method 4 failed: {str(e)}"
            logger.warning(error_msg)
            error_messages.append(error_msg)
        
        # Method 5: Try to download manually if possible
        try:
            logger.info("Method 5: Using manually downloaded ChromeDriver")
            # Create a directory for the driver if it doesn't exist
            driver_dir = os.path.join(os.path.expanduser("~"), "chromedriver")
            os.makedirs(driver_dir, exist_ok=True)
            
            driver_path = os.path.join(driver_dir, "chromedriver.exe" if platform.system() == "Windows" else "chromedriver")
            
            # Check if driver already exists
            if not os.path.isfile(driver_path):
                logger.warning(f"ChromeDriver not found at {driver_path}. Please download manually.")
                logger.info("Visit https://chromedriver.chromium.org/downloads to download the correct version")
                logger.info(f"Save it to: {driver_path}")
            else:
                logger.info(f"Using existing ChromeDriver at {driver_path}")
                
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully with Method 5")
            return driver
        except Exception as e:
            error_msg = f"Method 5 failed: {str(e)}"
            logger.warning(error_msg)
            error_messages.append(error_msg)
        
        # Final error message with all attempts
        combined_error = "Failed to initialize Chrome driver after multiple attempts:\n" + "\n".join(error_messages)
        if "not a valid Win32 application" in " ".join(error_messages):
            combined_error += "\n\nThe error suggests a mismatch between ChromeDriver and your Chrome version or system architecture. Please:"
            combined_error += "\n1. Make sure you have Chrome installed and up to date"
            combined_error += "\n2. Check if you're using a 32-bit or 64-bit system and match the ChromeDriver accordingly"
            combined_error += "\n3. Try downloading the ChromeDriver manually from https://chromedriver.chromium.org/downloads"
            combined_error += f"\n4. Save it to: {os.path.join(os.path.expanduser('~'), 'chromedriver', 'chromedriver.exe')}"
        
        logger.error(combined_error)
        raise Exception(combined_error)
    
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
            
            # If using Chrome profile, check if already logged in
            if self.use_chrome_profile:
                try:
                    # Check for elements that indicate we're logged in - looking for input fields
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Describe')]"))
                    )
                    logger.info("Already logged in via Chrome profile")
                    self.logged_in = True
                    return True
                except TimeoutException:
                    logger.info("Not logged in via Chrome profile, proceeding with Google login")
                    
                    # Find and click the Google login button
                    try:
                        # Look for the login button
                        login_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Log in')]")
                        if login_buttons:
                            logger.info("Clicking Log in button")
                            self._human_move_and_click(login_buttons[0])
                            time.sleep(2)
                        
                        # Look for Google login button
                        google_login = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Google') or contains(@class, 'google')]"))
                        )
                        logger.info("Clicking Google login button")
                        self._human_move_and_click(google_login)
                        
                        # Since we're using Chrome profile, Google might auto-login
                        # Give it time to process the Google authentication
                        logger.info("Waiting for Google authentication to complete...")
                        time.sleep(10)
                        
                        # Check if we're logged in by looking for the input field
                        WebDriverWait(self.driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Describe')]"))
                        )
                        
                        logger.info("Successfully logged in with Google")
                        self.logged_in = True
                        return True
                    except Exception as e:
                        logger.error(f"Google login failed: {str(e)}")
                        self.connection_error = f"Google login failed: {str(e)}"
                        return False
            
            # Traditional login path (email/password)
            if not self.use_chrome_profile and self.email and self.password:
                try:
                    # Click the login button
                    login_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Log in')]")
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
                    submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Log in') or contains(text(), 'Sign in')]")
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
            
            # Wait for successful login (check for input field)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Describe')]"))
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
            
            # Take a screenshot for debugging
            screenshot_path = os.path.join(os.path.expanduser("~"), "suno_debug_create.png")
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Create page screenshot saved to {screenshot_path}")
            
            # Find the prompt input field (main textarea)
            try:
                # Look for the main input textarea
                prompt_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'Describe')]"))
                )
                logger.info("Found prompt textarea")
                
                # Click and enter text
                self._human_move_and_click(prompt_field)
                prompt_field.clear()
                self._human_type(prompt_field, prompt)
                logger.info("Entered prompt text")
                
                # Find and click on details/advanced options if available
                try:
                    details_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Details') or contains(text(), 'Advanced') or contains(text(), 'Options')]"
                    )
                    if details_buttons:
                        logger.info("Clicking Details/Advanced button")
                        self._human_move_and_click(details_buttons[0])
                        time.sleep(1)
                except Exception as e:
                    logger.warning(f"Could not find Details button: {e}")
                
                # Enter style if provided (find the style input)
                if style:
                    try:
                        # Find inputs that might be for style
                        style_inputs = self.driver.find_elements(By.XPATH, 
                            "//textarea[contains(@placeholder, 'style') or contains(@placeholder, 'Style')]"
                        )
                        if not style_inputs:
                            # Try to find any secondary textarea
                            style_inputs = self.driver.find_elements(By.XPATH, "//textarea")
                            if len(style_inputs) > 1:
                                style_inputs = [style_inputs[1]]  # Use the second textarea
                        
                        if style_inputs:
                            logger.info(f"Found style input, entering: {style}")
                            style_input = style_inputs[0]
                            self._human_move_and_click(style_input)
                            style_input.clear()
                            self._human_type(style_input, style)
                    except Exception as e:
                        logger.warning(f"Failed to enter style: {e}")
                
                # Enter title if provided
                if title:
                    try:
                        # Find inputs that might be for title
                        title_inputs = self.driver.find_elements(By.XPATH, 
                            "//input[contains(@placeholder, 'title') or contains(@placeholder, 'Title')]"
                        )
                        if title_inputs:
                            logger.info(f"Found title input, entering: {title}")
                            title_input = title_inputs[0]
                            self._human_move_and_click(title_input)
                            title_input.clear()
                            self._human_type(title_input, title)
                    except Exception as e:
                        logger.warning(f"Failed to enter title: {e}")
                
                # Find the instrumental toggle if option is specified
                if instrumental is not None:
                    try:
                        # Find labels or spans with "Instrumental" text
                        instrumental_elements = self.driver.find_elements(By.XPATH, 
                            "//span[contains(text(), 'Instrumental')] | //label[contains(text(), 'Instrumental')]"
                        )
                        
                        if instrumental_elements:
                            instrumental_element = instrumental_elements[0]
                            logger.info(f"Found instrumental toggle, setting to: {instrumental}")
                            
                            # Find the closest toggle/switch element
                            parent = instrumental_element
                            for _ in range(3):  # Go up a few levels
                                if parent.tag_name != "body":
                                    parent = parent.find_element(By.XPATH, "..")
                            
                            # Look for a toggle element
                            toggle = parent.find_element(By.XPATH, 
                                ".//button[contains(@role, 'switch')] | .//div[contains(@class, 'switch')] | .//label[contains(@class, 'switch')]"
                            )
                            
                            # Check current state
                            toggle_classes = toggle.get_attribute("class")
                            toggle_aria = toggle.get_attribute("aria-checked")
                            
                            if toggle_aria:
                                # Use aria-checked if available
                                current_state = toggle_aria.lower() == "true"
                            else:
                                # Fallback to class checking
                                current_state = "bg-primary" in toggle_classes or "active" in toggle_classes or "checked" in toggle_classes
                            
                            logger.info(f"Current toggle state detected as: {current_state}")
                            
                            # Only click if the current state doesn't match desired state
                            if current_state != instrumental:
                                logger.info(f"Clicking instrumental toggle")
                                self._human_move_and_click(toggle)
                                time.sleep(1)
                    except Exception as e:
                        logger.warning(f"Failed to set instrumental mode: {e}")
                
                # Take another screenshot after filling the form
                self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_filled.png"))
                
                # Find and click the generate/create button
                create_button = None
                button_selectors = [
                    "//button[contains(text(), 'Create')]",
                    "//button[contains(text(), 'Generate')]",
                    "//button[contains(@class, 'primary')]",
                    "//button[contains(@type, 'submit')]"
                ]
                
                for selector in button_selectors:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            create_button = button
                            break
                    if create_button:
                        break
                
                if not create_button:
                    logger.error("Could not find the create/generate button")
                    return {"success": False, "error": "Could not find the create button"}
                
                logger.info("Clicking create button")
                self._human_move_and_click(create_button)
                
                # Wait for generation to complete
                logger.info("Waiting for song generation to complete...")
                
                # Wait for the generating indicator to disappear
                try:
                    generating_selectors = [
                        "//div[contains(text(), 'Generating')]",
                        "//div[contains(text(), 'Processing')]",
                        "//div[contains(@class, 'loading')]",
                        "//div[contains(@class, 'spinner')]",
                        "//span[contains(text(), 'Creating')]"
                    ]
                    
                    for selector in generating_selectors:
                        try:
                            generating_elements = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            logger.info(f"Found generation indicator with selector: {selector}")
                            
                            # Wait for it to disappear
                            WebDriverWait(self.driver, 300).until_not(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            break
                        except TimeoutException:
                            continue
                except TimeoutException:
                    logger.warning("Generation might still be in progress, but continuing...")
                
                # Wait for share or download buttons to appear
                logger.info("Waiting for playback controls to appear...")
                
                # Look for play buttons or audio elements
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//button[contains(@aria-label, 'Play')] | //audio | //div[contains(@class, 'player')]"
                    ))
                )
                
                logger.info("Song generation completed")
                
                # Get the song URL
                song_url = self.driver.current_url
                logger.info(f"Generated song URL: {song_url}")
                
                # Take a final screenshot
                self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_complete.png"))
                
                return {
                    "success": True, 
                    "url": song_url, 
                    "prompt": prompt, 
                    "style": style, 
                    "title": title
                }
            except Exception as e:
                logger.error(f"Failed to interact with create form: {str(e)}")
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
            
            # Look for download button
            download_buttons = []
            download_selectors = [
                "//button[contains(text(), 'Download')]", 
                "//button[contains(@aria-label, 'Download')]",
                "//div[contains(text(), 'Download')]",
                "//span[contains(text(), 'Download')]"
            ]
            
            for selector in download_selectors:
                buttons = self.driver.find_elements(By.XPATH, selector)
                download_buttons.extend([b for b in buttons if b.is_displayed()])
            
            if not download_buttons:
                logger.error("No download button found")
                return {"success": False, "error": "Download button not found"}
                
            logger.info(f"Found {len(download_buttons)} download buttons. Clicking the first one.")
            self._human_move_and_click(download_buttons[0])
            
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
