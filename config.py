
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_config():
    """Load configuration from .env file or environment variables"""
    # Load .env file if it exists
    load_dotenv()
    
    # Required variables - email and password are now optional if using Chrome profile
    config = {}
    
    # Check if using Chrome profile
    use_chrome_profile = os.environ.get("USE_CHROME_PROFILE", "False").lower() == "true"
    config["USE_CHROME_PROFILE"] = use_chrome_profile
    
    if use_chrome_profile:
        # Chrome profile path is required if using Chrome profile
        chrome_user_data_dir = os.environ.get("CHROME_USER_DATA_DIR")
        if not chrome_user_data_dir:
            logger.error("Missing required environment variable: CHROME_USER_DATA_DIR")
            raise ValueError("Missing required environment variable: CHROME_USER_DATA_DIR")
        config["CHROME_USER_DATA_DIR"] = chrome_user_data_dir
    else:
        # If not using Chrome profile, email and password are required
        required_vars = ["EMAIL", "PASSWORD"]
        for var in required_vars:
            value = os.environ.get(var)
            if not value:
                logger.error(f"Missing required environment variable: {var}")
                raise ValueError(f"Missing required environment variable: {var}")
            config[var] = value
    
    # Optional variables
    optional_vars = ["HEADLESS", "DOWNLOAD_PATH"]
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            config[var] = value
    
    return config
