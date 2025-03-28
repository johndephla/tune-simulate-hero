
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
        # ... keep existing code (Chrome driver setup logic)
    
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
            
            # First, let's try to find the main prompt textarea (this is at the bottom of the page)
            try:
                # Look for the main prompt textarea. There are multiple textareas in the UI now
                prompt_textareas = self.driver.find_elements(By.CSS_SELECTOR, "textarea")
                
                # The main prompt textarea is the largest one - usually the last in the DOM
                prompt_textarea = None
                for textarea in prompt_textareas:
                    # Check if this textarea is for the prompt (usually the largest or has a specific placeholder)
                    placeholder = textarea.get_attribute("placeholder")
                    if placeholder and ("Enter" in placeholder or "Describe" in placeholder):
                        if not prompt_textarea or textarea.size['height'] > prompt_textarea.size['height']:
                            prompt_textarea = textarea
                
                # If we still haven't found it, try getting the last textarea
                if not prompt_textarea and prompt_textareas:
                    prompt_textarea = prompt_textareas[-1]
                
                if prompt_textarea:
                    logger.info("Found main prompt textarea")
                    
                    # Scroll to the textarea
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", prompt_textarea)
                    time.sleep(1)
                    
                    # Click and enter text
                    self._human_move_and_click(prompt_textarea)
                    prompt_textarea.clear()
                    self._human_type(prompt_textarea, prompt)
                    logger.info("Entered prompt text")
                    
                    # Handle style input if provided
                    if style:
                        # Find the style textarea - usually the second textarea or one with specific placeholder
                        style_textarea = None
                        for textarea in prompt_textareas:
                            placeholder = textarea.get_attribute("placeholder")
                            if placeholder and ("style" in placeholder.lower() or "music" in placeholder.lower()):
                                style_textarea = textarea
                                break
                        
                        # If we've found a dedicated style textarea
                        if style_textarea and style_textarea != prompt_textarea:
                            logger.info(f"Found style textarea, entering: {style}")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", style_textarea)
                            time.sleep(1)
                            self._human_move_and_click(style_textarea)
                            style_textarea.clear()
                            self._human_type(style_textarea, style)
                        else:
                            logger.warning("Could not find a dedicated style textarea")
                            # Try to find any elements that might relate to style settings
                            style_elements = self.driver.find_elements(By.XPATH, 
                                "//*[contains(text(), 'Style of Music') or contains(text(), 'Music Style')]/following::textarea[1]"
                            )
                            if style_elements:
                                logger.info(f"Found style input through text search, entering: {style}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", style_elements[0])
                                time.sleep(1)
                                self._human_move_and_click(style_elements[0])
                                style_elements[0].clear()
                                self._human_type(style_elements[0], style)
                    
                    # Handle title input if provided
                    if title:
                        # Look for title input - could be a textarea or specific input field
                        title_elements = self.driver.find_elements(By.XPATH, 
                            "//*[contains(text(), 'Title')]/following::textarea[1] | //*[contains(text(), 'Title')]/following::input[1]"
                        )
                        
                        if title_elements:
                            logger.info(f"Found title input, entering: {title}")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", title_elements[0])
                            time.sleep(1)
                            self._human_move_and_click(title_elements[0])
                            title_elements[0].clear()
                            self._human_type(title_elements[0], title)
                        else:
                            # Try to find inputs with title placeholder
                            title_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                                "input[placeholder*='title' i], textarea[placeholder*='title' i]"
                            )
                            if title_inputs:
                                logger.info(f"Found title input by placeholder, entering: {title}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", title_inputs[0])
                                time.sleep(1)
                                self._human_move_and_click(title_inputs[0])
                                title_inputs[0].clear()
                                self._human_type(title_inputs[0], title)
                    
                    # Handle instrumental toggle
                    if instrumental is not None:
                        try:
                            # Find instrumental toggle by looking for text near it
                            instrumental_elements = self.driver.find_elements(By.XPATH, 
                                "//*[contains(text(), 'Instrumental')]"
                            )
                            
                            if instrumental_elements:
                                # Scroll to the element
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", instrumental_elements[0])
                                time.sleep(1)
                                
                                logger.info(f"Found instrumental text, looking for toggle nearby")
                                
                                # Look for toggle element nearby - various selectors to try
                                toggle_selectors = [
                                    "./ancestor::div[3]//div[contains(@class, 'toggle') or contains(@class, 'switch')]",
                                    "./ancestor::div[2]//div[@tabindex='0']",
                                    "./following::div[@tabindex='0'][1]",
                                    "./ancestor::div[3]//input[@type='checkbox']",
                                    "./ancestor::*[position()<=4]//div[@role='switch' or contains(@class, 'switch') or contains(@class, 'toggle')]"
                                ]
                                
                                toggle = None
                                for selector in toggle_selectors:
                                    try:
                                        toggle_candidates = instrumental_elements[0].find_elements(By.XPATH, selector)
                                        if toggle_candidates:
                                            toggle = toggle_candidates[0]
                                            break
                                    except:
                                        continue
                                
                                if toggle:
                                    # Try to determine the current state of the toggle
                                    current_state = None
                                    
                                    # Method 1: Check aria-checked attribute
                                    aria_checked = toggle.get_attribute("aria-checked")
                                    if aria_checked:
                                        current_state = aria_checked.lower() == "true"
                                        logger.info(f"Toggle state detected from aria-checked: {current_state}")
                                    
                                    # Method 2: Check class contains 'selected', 'active', etc.
                                    if current_state is None:
                                        toggle_class = toggle.get_attribute("class")
                                        if toggle_class:
                                            active_indicators = ["selected", "active", "checked", "translate-x-4", "translate-x-5"]
                                            inactive_indicators = ["translate-x-0", "translate-x-1"]
                                            
                                            for indicator in active_indicators:
                                                if indicator in toggle_class:
                                                    current_state = True
                                                    logger.info(f"Toggle state detected as ON from class: {toggle_class}")
                                                    break
                                                    
                                            if current_state is None:
                                                for indicator in inactive_indicators:
                                                    if indicator in toggle_class:
                                                        current_state = False
                                                        logger.info(f"Toggle state detected as OFF from class: {toggle_class}")
                                                        break
                                    
                                    # Method 3: Check background color if state still unknown
                                    if current_state is None:
                                        bg_color = toggle.value_of_css_property("background-color")
                                        if "255" in bg_color or "rgb(1" in bg_color:  # Brighter colors often indicate "on"
                                            current_state = True
                                        else:
                                            current_state = False
                                        logger.info(f"Toggle state guessed from background color: {current_state}")
                                    
                                    # Check if the toggle needs to be changed
                                    if current_state is not None and current_state != instrumental:
                                        logger.info(f"Changing instrumental toggle from {current_state} to {instrumental}")
                                        self._human_move_and_click(toggle)
                                        time.sleep(1)
                                    elif current_state is None:
                                        # If we can't determine the state, click it anyway if we want instrumental
                                        if instrumental:
                                            logger.info("Could not determine toggle state, clicking anyway")
                                            self._human_move_and_click(toggle)
                                            time.sleep(1)
                                    else:
                                        logger.info(f"Instrumental already set to {instrumental}, no action needed")
                        except Exception as e:
                            logger.warning(f"Failed to interact with instrumental toggle: {e}")
                    
                    # Take a screenshot after setting all parameters
                    self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "suno_debug_params_set.png"))
                    
                    # Find and click the generate/create button - it's usually at the bottom of the form
                    create_button = None
                    
                    # Try multiple approaches to find the button
                    button_locators = [
                        (By.XPATH, "//button[contains(text(), 'Create')]"),
                        (By.XPATH, "//button[contains(@class, 'buttonAnimate')]"),
                        (By.XPATH, "//button[contains(text(), 'Create')]/ancestor::div[contains(@class, 'create-button')]"),
                        (By.CSS_SELECTOR, ".buttonAnimate"),
                        (By.XPATH, "//div[contains(@class, 'create-button')]//button"),
                        (By.XPATH, "//button[.//svg and .//span[contains(text(), 'Create')]]")
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
                        logger.warning("Create button is disabled. Checking for input errors or limitations.")
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
