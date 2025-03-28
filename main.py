
import os
import sys
import logging
import threading
import time
import uvicorn
from api_server import app
from browser_automation import SunoAutomation
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("suno_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def start_api_server():
    """Start the FastAPI server in a separate thread"""
    logger.info("Starting API server at http://0.0.0.0:8000")
    try:
        # Use 0.0.0.0 instead of 127.0.0.1 to allow connections from other machines
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        logger.error(f"Failed to start API server: {str(e)}")
        print(f"Error starting API server: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Suno.ai Automation")
    
    # Load configuration
    config = get_config()
    
    # Create automation instance
    try:
        if config.get("USE_CHROME_PROFILE", True):
            logger.info("Using Chrome profile for authentication")
            chrome_user_data_dir = config.get("CHROME_USER_DATA_DIR")
            
            if not chrome_user_data_dir or not os.path.exists(chrome_user_data_dir):
                logger.warning(f"Chrome user data directory not found: {chrome_user_data_dir}")
                print(f"Warning: Chrome profile directory not found at: {chrome_user_data_dir}")
                print("Using default profile path or checking for email/password instead")
                
                if config.get("EMAIL") and config.get("PASSWORD"):
                    logger.info("Falling back to email/password authentication")
                    automation = SunoAutomation(
                        email=config.get("EMAIL"),
                        password=config.get("PASSWORD"),
                        headless=config.get("HEADLESS", "False").lower() == "true"
                    )
                else:
                    # Try with Chrome profile anyway (might be a new profile)
                    automation = SunoAutomation(
                        headless=config.get("HEADLESS", "False").lower() == "true",
                        use_chrome_profile=True,
                        chrome_user_data_dir=chrome_user_data_dir
                    )
            else:
                automation = SunoAutomation(
                    headless=config.get("HEADLESS", "False").lower() == "true",
                    use_chrome_profile=True,
                    chrome_user_data_dir=chrome_user_data_dir
                )
        elif config.get("EMAIL") and config.get("PASSWORD"):
            logger.info("Using email/password for authentication")
            automation = SunoAutomation(
                email=config.get("EMAIL"),
                password=config.get("PASSWORD"),
                headless=config.get("HEADLESS", "False").lower() == "true"
            )
        else:
            logger.error("Neither Chrome profile nor email/password authentication information provided")
            print("Error: Authentication information is missing.")
            print("Please configure either:")
            print("1. Chrome profile: Create a .env file with USE_CHROME_PROFILE=True and CHROME_USER_DATA_DIR set")
            print("2. Email/password: Add EMAIL and PASSWORD to your .env file")
            print("\nDefault Chrome profile path will be attempted, but may not work if Chrome is running")
            print("with a different profile or if you need to log in first.")
            
            # Try with default Chrome profile as a last resort
            automation = SunoAutomation(
                headless=config.get("HEADLESS", "False").lower() == "true",
                use_chrome_profile=True,
                chrome_user_data_dir=config.get("CHROME_USER_DATA_DIR")
            )
    
        # Check if automation initialized correctly
        if not automation.connected:
            logger.warning("Selenium automation connected but in a warning state. Check for errors.")
            print("Warning: Selenium connected but may have initialization issues.")
            print(f"Error details: {automation.connection_error}")
        else:
            logger.info("Selenium automation initialized successfully")
    
        # Store automation instance in app state for API access
        app.state.automation = automation
        
        # Start API server in a separate thread
        server_thread = threading.Thread(target=start_api_server, daemon=True)
        server_thread.start()
        
        logger.info(f"API server started at http://0.0.0.0:8000")
        print(f"API server started at http://0.0.0.0:8000")
        print("React frontend can now connect to the API")
        print("Press Ctrl+C to exit")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            automation.close()
            sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to initialize automation: {str(e)}")
        print(f"Error: {str(e)}")
        print("Please check your configuration and try again.")
        sys.exit(1)
