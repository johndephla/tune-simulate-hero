
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_config():
    """Load configuration from .env file or environment variables"""
    # Load .env file if it exists
    load_dotenv()
    
    required_vars = ["EMAIL", "PASSWORD"]
    config = {}
    
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
