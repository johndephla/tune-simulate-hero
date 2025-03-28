
import os
import logging
import platform
import sys
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_default_chrome_profile_dir():
    """Get the default Chrome user data directory based on OS"""
    if platform.system() == "Windows":
        # Check multiple common locations
        possible_paths = [
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"),
            r"C:\Program Files\Google\Chrome\User Data",
            r"C:\Program Files (x86)\Google\Chrome\User Data"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found existing Chrome profile at: {path}")
                return path
                
        # Default path even if it doesn't exist
        return os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
        
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome")
    else:  # Linux
        # Check multiple common Linux paths
        possible_paths = [
            os.path.join(os.path.expanduser("~"), ".config", "google-chrome"),
            os.path.join(os.path.expanduser("~"), ".config", "chromium")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Default to Chrome path
        return os.path.join(os.path.expanduser("~"), ".config", "google-chrome")

def get_default_driver_path():
    """Get the default chromedriver path based on OS"""
    driver_dir = os.path.join(os.path.expanduser("~"), "chromedriver")
    if platform.system() == "Windows":
        return os.path.join(driver_dir, "chromedriver.exe")
    else:
        return os.path.join(driver_dir, "chromedriver")

def get_config():
    """Load configuration from .env file or environment variables"""
    # Load .env file if it exists
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        logger.info(f"Loading configuration from .env file: {env_path}")
        load_dotenv(env_path)
    else:
        logger.warning(f".env file not found at {env_path}")
        logger.info("Using environment variables or defaults")
    
    # Initialize config dictionary
    config = {}
    
    # Check if using Chrome profile
    use_chrome_profile = os.environ.get("USE_CHROME_PROFILE", "True").lower() == "true"  # Default to True
    config["USE_CHROME_PROFILE"] = use_chrome_profile
    
    # Add Chrome profile path if using Chrome profile
    if use_chrome_profile:
        # Default to standard Chrome profile location based on OS
        default_path = get_default_chrome_profile_dir()
        chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR", default_path)
        
        # Verifica se la directory esiste
        if not os.path.exists(chrome_user_data_dir):
            logger.warning(f"Chrome profile directory does not exist: {chrome_user_data_dir}")
            logger.info(f"Will create a new profile directory when Chrome is launched")
            
            # Try to create the directory
            try:
                os.makedirs(chrome_user_data_dir, exist_ok=True)
                logger.info(f"Created Chrome profile directory: {chrome_user_data_dir}")
            except Exception as e:
                logger.warning(f"Failed to create Chrome profile directory: {str(e)}")
        
        config["CHROME_USER_DATA_DIR"] = chrome_user_data_dir
        logger.info(f"Using Chrome profile from: {chrome_user_data_dir}")
    
    # Add email and password if provided (now optional)
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    if email:
        config["EMAIL"] = email
    if password:
        config["PASSWORD"] = password
    
    # Add ChromeDriver path if specified
    driver_path = os.environ.get("CHROMEDRIVER_PATH", get_default_driver_path())
    config["CHROMEDRIVER_PATH"] = driver_path
    
    # Check if driver exists
    if os.path.exists(driver_path):
        logger.info(f"ChromeDriver found at: {driver_path}")
    else:
        logger.warning(f"ChromeDriver not found at: {driver_path}")
        logger.info("Will attempt to download driver automatically or use system driver")
    
    # Add optional variables
    optional_vars = ["HEADLESS", "DOWNLOAD_PATH"]
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            config[var] = value
    
    # Use debug mode by default in development
    debug_mode = os.environ.get("DEBUG", "True").lower() == "true"
    config["DEBUG"] = debug_mode
    
    return config
