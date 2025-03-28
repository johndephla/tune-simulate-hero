
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_config():
    """Load configuration from .env file or environment variables"""
    # Load .env file if it exists
    load_dotenv()
    
    # Initialize config dictionary
    config = {}
    
    # Check if using Chrome profile
    use_chrome_profile = os.environ.get("USE_CHROME_PROFILE", "True").lower() == "true"  # Default to True
    config["USE_CHROME_PROFILE"] = use_chrome_profile
    
    # Add Chrome profile path if using Chrome profile
    if use_chrome_profile:
        # Default to standard Chrome profile location for Windows
        default_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
        chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR", default_path)
        config["CHROME_USER_DATA_DIR"] = chrome_user_data_dir
        logger.info(f"Using Chrome profile from: {chrome_user_data_dir}")
    
    # Add email and password if provided (now optional)
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    if email:
        config["EMAIL"] = email
    if password:
        config["PASSWORD"] = password
    
    # Add optional variables
    optional_vars = ["HEADLESS", "DOWNLOAD_PATH"]
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            config[var] = value
    
    return config
