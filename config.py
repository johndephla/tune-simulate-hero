
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
    use_chrome_profile = os.environ.get("USE_CHROME_PROFILE", "False").lower() == "true"
    config["USE_CHROME_PROFILE"] = use_chrome_profile
    
    # Add Chrome profile path if using Chrome profile
    if use_chrome_profile:
        chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR")
        if not chrome_user_data_dir:
            logger.warning("USE_CHROME_PROFILE is True but CHROME_USER_DATA_DIR is not set")
            print("Warning: CHROME_USER_DATA_DIR is required when USE_CHROME_PROFILE=True")
            print("Please set CHROME_USER_DATA_DIR in your .env file")
        config["CHROME_USER_DATA_DIR"] = chrome_user_data_dir
    
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
