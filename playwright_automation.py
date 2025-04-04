
import asyncio
import logging
import os
import platform
import random
import tempfile
import time
from typing import Dict, Any, Optional, List

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, ElementHandle
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SunoAutomation:
    """Class to automate interactions with Suno.com using Playwright"""
    
    def __init__(self, email=None, password=None, headless=False, use_chrome_profile=False, chrome_user_data_dir=None):
        self.email = email
        self.password = password
        self.logged_in = False
        self.headless = headless
        self.use_chrome_profile = use_chrome_profile
        self.chrome_user_data_dir = chrome_user_data_dir
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.connected = False
        self.connection_error = None
        
        try:
            # Connect to browser using sync API instead of async
            self._setup_browser()
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            self.connection_error = str(e)
            self.connected = False
    
    def _setup_browser(self):
        """Set up and configure the Playwright browser using sync API"""
        try:
            # Start Playwright with sync API
            self.playwright = sync_playwright().start()
            
            # Browser launch options
            browser_args = []
            browser_kwargs = {
                "headless": self.headless
            }
            
            # Set up Chrome profile if requested
            if self.use_chrome_profile and self.chrome_user_data_dir:
                logger.info(f"Using Chrome profile from: {self.chrome_user_data_dir}")
                browser_kwargs["user_data_dir"] = self.chrome_user_data_dir
            
            # Launch browser - using chromium for better compatibility
            self.browser = self.playwright.chromium.launch(**browser_kwargs)
            
            # Create a new browser context
            context_options = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
                "ignore_https_errors": True
            }
            
            # Create download directory
            download_dir = tempfile.mkdtemp()
            context_options["accept_downloads"] = True
            
            self.context = self.browser.new_context(**context_options)
            
            # Create a new page
            self.page = self.context.new_page()
            
            # Set default timeout to 30 seconds (more generous than Selenium default)
            self.page.set_default_timeout(30000)
            
            return True
        except Exception as e:
            logger.error(f"Browser setup failed: {str(e)}")
            # Clean up resources if initialization fails
            self._cleanup()
            raise e
    
    def _log_request(self, route, request):
        """Log request details for debugging purposes"""
        logger.debug(f"Request: {request.method} {request.url}")
        route.continue_()
    
    def _cleanup(self):
        """Close browser and clean up resources"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def _random_wait(self, min_seconds=0.5, max_seconds=2.0):
        """Wait for a random amount of time to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _human_type(self, element, text):
        """Type text like a human with random delays"""
        if not text:
            return
            
        for char in text:
            element.type(char, delay=random.uniform(50, 150))
            # Random pause between characters (50-150ms)
    
    def is_connected(self):
        """Check if browser is connected and working"""
        return self.connected and self.browser is not None
    
    def get_status(self):
        """Get current status of the browser automation"""
        return {
            "connected": self.connected,
            "logged_in": self.logged_in,
            "error": self.connection_error
        }
    
    def login(self):
        """Login to Suno.com"""
        if not self.connected:
            logger.error("Browser not connected, can't login")
            return False
            
        if self.logged_in:
            logger.info("Already logged in")
            return True
        
        return self._login_sync()
    
    def _login_sync(self):
        """Synchronous implementation of login"""
        logger.info("Navigating to Suno.com")
        try:
            # Navigate to Suno.com
            self.page.goto("https://suno.com/create?wid=default", wait_until="domcontentloaded")
            
            # Check if already logged in by looking for the prompt textarea
            try:
                textarea = self.page.wait_for_selector('textarea[placeholder="Enter style of music"]', timeout=5000)
                if textarea:
                    logger.info("Already logged in via Chrome profile")
                    self.logged_in = True
                    return True
            except Exception:
                logger.info("Not logged in yet, proceeding with authentication")
            
            # If using Chrome profile, handle login
            if self.use_chrome_profile:
                try:
                    # Look for login/sign-in button
                    login_button = self.page.query_selector('button:has-text("Log in"), button:has-text("Sign in")')
                    
                    if login_button:
                        logger.info("Clicking Log in button")
                        login_button.click()
                        self._random_wait(1, 2)
                    
                    # Look for Google login button
                    google_login = self.page.wait_for_selector('button:has-text("Google"), button:has-text("Continue with Google")', timeout=10000)
                    if google_login:
                        logger.info("Clicking Google login button")
                        google_login.click()
                        
                        # Since we're using Chrome profile, Google might auto-login
                        # Give it time to process the Google authentication
                        logger.info("Waiting for Google authentication to complete...")
                        self._random_wait(5, 10)
                except Exception as e:
                    logger.error(f"Google login failed: {str(e)}")
            
            # Traditional login path (email/password)
            elif self.email and self.password:
                try:
                    # Click the login button
                    login_button = self.page.query_selector('button:has-text("Log in"), button:has-text("Sign in")')
                    
                    if login_button:
                        logger.info("Clicking Log in button")
                        login_button.click()
                        self._random_wait(1, 2)
                    
                    # Try to find the email login option
                    email_option = self.page.query_selector('button:has-text("Email")')
                    if email_option:
                        logger.info("Clicking Email login option")
                        email_option.click()
                        self._random_wait(1, 2)
                    
                    # Wait for email field and enter email
                    email_field = self.page.wait_for_selector('input[type="email"], input[name="email"]', timeout=10000)
                    if email_field:
                        logger.info("Entering email")
                        self._human_type(email_field, self.email)
                        
                        # Find continue button and click it
                        continue_button = self.page.query_selector('button:has-text("Continue")')
                        if continue_button:
                            logger.info("Clicking Continue button")
                            continue_button.click()
                            self._random_wait(1, 2)
                    
                    # Wait for password field and enter password
                    password_field = self.page.wait_for_selector('input[type="password"], input[name="password"]', timeout=10000)
                    if password_field:
                        logger.info("Entering password")
                        self._human_type(password_field, self.password)
                        
                        # Click submit/login button
                        submit_button = self.page.query_selector('button:has-text("Log in"), button:has-text("Sign in")')
                        if submit_button:
                            logger.info("Clicking final login button")
                            submit_button.click()
                            self._random_wait(3, 5)
                except Exception as e:
                    logger.error(f"Email/password login steps failed: {str(e)}")
            else:
                # Give user time to complete login if needed
                logger.info("Waiting for user to complete login manually...")
                self._random_wait(10, 15)
            
            # Final check - wait for the presence of textarea to confirm login
            try:
                self.page.wait_for_selector('textarea', timeout=20000)
                logger.info("Successfully logged in")
                self.logged_in = True
                return True
            except Exception as e:
                logger.error(f"Login verification failed: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.connection_error = f"Login failed: {str(e)}"
            self.logged_in = False
            return False
    
    def generate_song(self, prompt, style=None, title=None, instrumental=True):
        """Generate a song with the given parameters"""
        if not self.connected:
            logger.error("Browser not connected, can't generate song")
            return {"success": False, "error": "Browser not connected"}
            
        logger.info(f"Generating song with prompt: {prompt}, style: {style}, title: {title}, instrumental: {instrumental}")
        
        if not self.logged_in:
            if not self.login():
                return {"success": False, "error": "Login failed"}
        
        return self._generate_song_sync(prompt, style, title, instrumental)
    
    def _generate_song_sync(self, prompt, style=None, title=None, instrumental=True):
        """Synchronous implementation of song generation"""
        try:
            # Navigate to create page if not already there
            if "create" not in self.page.url:
                self.page.goto("https://suno.com/create?wid=default", wait_until="domcontentloaded")
                self._random_wait(2, 3)
                logger.info("Navigated to the create page")
            
            # Take a screenshot for debugging
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_path = os.path.join(os.path.expanduser("~"), f"suno_debug_create_{timestamp}.png")
            self.page.screenshot(path=screenshot_path)
            logger.info(f"Create page screenshot saved to {screenshot_path}")
            
            # Set the style (if provided)
            if style:
                try:
                    # Look for style textarea using the selector provided
                    style_textarea = self.page.wait_for_selector('textarea[placeholder="Enter style of music"]', timeout=5000)
                    if style_textarea:
                        logger.info(f"Found style textarea, entering: {style}")
                        style_textarea.click()
                        style_textarea.fill("")  # Clear existing text
                        self._human_type(style_textarea, style)
                except Exception as e:
                    logger.warning(f"Could not set style: {str(e)}")
            
            # Set the title (if provided)
            if title:
                try:
                    # Look for title textarea using the selector provided
                    title_textarea = self.page.wait_for_selector('textarea[placeholder="Enter a title"]', timeout=5000)
                    if title_textarea:
                        logger.info(f"Found title textarea, entering: {title}")
                        title_textarea.click()
                        title_textarea.fill("")  # Clear existing text
                        self._human_type(title_textarea, title)
                except Exception as e:
                    logger.warning(f"Could not set title: {str(e)}")
            
            # Set instrumental mode
            try:
                # Find the instrumental toggle
                toggle_container = self.page.wait_for_selector('div[aria-label="Instrumental"]', timeout=5000)
                if toggle_container:
                    # Check if it's already in the correct state
                    toggle_span = toggle_container.query_selector("span")
                    is_active = False
                    
                    if toggle_span:
                        class_attr = toggle_span.get_attribute("class")
                        is_active = class_attr and "translate-x-4" in class_attr
                    
                    logger.info(f"Instrumental toggle current state: {'active' if is_active else 'inactive'}")
                    
                    # Click only if we need to change the state
                    if is_active != instrumental:
                        logger.info(f"Clicking instrumental toggle to change from {is_active} to {instrumental}")
                        toggle_container.click()
                        self._random_wait(1, 2)
                    else:
                        logger.info(f"Instrumental toggle already in desired state: {instrumental}")
            except Exception as e:
                logger.warning(f"Could not set instrumental mode: {str(e)}")
            
            # Find and enter the main prompt
            try:
                # Focus on the main textarea (using the sibling relationship with the Create button)
                main_textarea = self.page.wait_for_selector('textarea', timeout=5000)
                if main_textarea:
                    logger.info("Found main prompt textarea")
                    main_textarea.click()
                    main_textarea.fill("")  # Clear existing text
                    self._human_type(main_textarea, prompt)
                    logger.info("Entered prompt text")
                else:
                    logger.error("Could not find main prompt textarea")
                    return {"success": False, "error": "Could not find prompt textarea"}
            except Exception as e:
                logger.error(f"Failed to enter prompt: {str(e)}")
                return {"success": False, "error": f"Failed to enter prompt: {str(e)}"}
            
            # Take screenshot before clicking Create button
            self.page.screenshot(path=os.path.join(os.path.expanduser("~"), "suno_debug_before_click.png"))
            
            # Find and click the create button
            try:
                # Try different selectors for the Create button
                create_button = None
                
                # Try to find by class name and text
                button_with_text = self.page.query_selector('.buttonAnimate >> text=Create')
                if button_with_text:
                    create_button = button_with_text
                
                # If not found, try by role
                if not create_button:
                    create_button = self.page.query_selector('button:has-text("Create")')
                
                if not create_button:
                    logger.error("Could not find the Create button")
                    return {"success": False, "error": "Could not find the Create button"}
                
                # Check if the button is disabled
                is_disabled = create_button.get_attribute("disabled")
                if is_disabled:
                    logger.warning("Create button is disabled. This could be due to input errors or account limitations.")
                    return {"success": False, "error": "Create button is disabled. You may need to check inputs or account limitations."}
                
                logger.info("Clicking Create button")
                create_button.click()
                
                # Wait for generation to start and complete
                logger.info("Waiting for song generation to begin...")
                
                # Wait for indicators that generation has started
                generation_started = False
                for indicator in ["text=Creating", "text=Generating", ".loading", ".spinner", "text=Please wait"]:
                    try:
                        self.page.wait_for_selector(indicator, timeout=10000, state="visible")
                        generation_started = True
                        logger.info(f"Song generation started (detected indicator: {indicator})")
                        break
                    except Exception:
                        continue
                
                if not generation_started:
                    logger.warning("Did not detect generation start indicators - continuing anyway")
                
                # Wait for indicators that generation is complete
                completion_indicators = [
                    '[aria-label="Play"]',
                    '.player',
                    'audio',
                    '[aria-label="Download"]',
                    'button:has-text("Download")',
                    'button:has-text("Share")'
                ]
                
                generation_completed = False
                for indicator in completion_indicators:
                    try:
                        self.page.wait_for_selector(indicator, timeout=300000)  # 5 minutes timeout
                        generation_completed = True
                        logger.info(f"Song generation completed (detected indicator: {indicator})")
                        break
                    except Exception:
                        continue
                
                if not generation_completed:
                    logger.error("Song generation timed out or failed")
                    return {"success": False, "error": "Song generation timed out"}
                
                # Take a final screenshot
                self.page.screenshot(path=os.path.join(os.path.expanduser("~"), "suno_debug_complete.png"))
                
                # Get the song URL
                song_url = self.page.url
                logger.info(f"Generated song URL: {song_url}")
                
                return {
                    "success": True, 
                    "url": song_url, 
                    "prompt": prompt, 
                    "style": style, 
                    "title": title
                }
                
            except Exception as e:
                logger.error(f"Failed to generate song: {str(e)}")
                return {"success": False, "error": str(e)}
                
        except Exception as e:
            logger.error(f"Song generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def download_song(self, song_url=None):
        """Download the generated song"""
        logger.info("Attempting to download song")
        
        return self._download_song_sync(song_url)
    
    def _download_song_sync(self, song_url=None):
        """Synchronous implementation of song download"""
        try:
            if song_url:
                self.page.goto(song_url, wait_until="domcontentloaded")
                self._random_wait(2, 3)
            
            # Take a screenshot to debug download process
            self.page.screenshot(path=os.path.join(os.path.expanduser("~"), "suno_debug_download.png"))
            
            # Set up download location
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(download_path):
                os.makedirs(download_path)
            
            # Look for download button
            download_selectors = [
                'button:has-text("Download")', 
                '[aria-label="Download"]',
                'a[download]'  # Direct download links
            ]
            
            download_element = None
            for selector in download_selectors:
                try:
                    element = self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        download_element = element
                        break
                except Exception:
                    continue
            
            if not download_element:
                logger.error("No download button found")
                return {"success": False, "error": "Download button not found"}
                
            logger.info(f"Found download element, attempting to click")
            
            # Start waiting for download
            with self.page.expect_download() as download_info:
                download_element.click()
                download = download_info.value
                
                # Wait for download to complete
                path = download.path()
                
                # Save to downloads folder
                suggested_filename = download.suggested_filename
                save_path = os.path.join(download_path, suggested_filename)
                
                download.save_as(save_path)
                logger.info(f"File downloaded to: {save_path}")
                
                return {"success": True, "file_path": save_path}
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the browser and clean up"""
        logger.info("Closing browser")
        self._cleanup()
        self.connected = False
        self.logged_in = False
